#!/usr/bin/env python3
"""Run the frozen PA modern-model screen with a durable request ledger.

This runner is intentionally PA-specific and provider-neutral at the ledger
boundary.  It consumes the private render manifest produced by
``render_modern_views.py``, sends no Gemini 2.0 request, and stores raw provider
bodies outside Git.  ``--authorize-live`` is required for every provider call;
the flag writes an ignored timestamped authorization record for the project
manager's audit trail.

Examples (PowerShell, using the bundled runtime):

    $env:PYTHONPATH = "src;local_agent/runtime/python_deps"
    $env:AI_GATEWAY_GEMINI_BASE = "<private-gemini-gateway-base>"
    $env:AI_GATEWAY_QWEN_BASE = "<private-qwen-gateway-base>"
    python scripts/run_modern_screen.py --smoke --authorize-live \
      --render-manifest path/to/private/render_manifest.csv

    python scripts/run_modern_screen.py --full --authorize-live \
      --render-manifest path/to/private/render_manifest.csv

The Qwen path performs at most 81 serialized warmup attempts and never runs a
concurrent keepalive during scored traffic.  Resume is fingerprint-guarded:
matching terminal rows are skipped, while ambiguous submissions stop the run.
"""

from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import io
import json
import os
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx
from PIL import Image

from icdar_tta.parser import PA_V149_REQUIRED_FIELDS, parse_response_json
from icdar_tta.request_ledger import (
    LEDGER_SCHEMA_VERSION,
    validate_history,
    validate_record,
    request_fingerprint,
    read_ledger,
)


MODELS = {
    "gemini-3.7-flash": "gemini",
    "gemini-3.5-flash": "gemini",
    "gemini-3.5-flash-lite": "gemini",
    "sagemaker-qwen3-vl-8b-instruct-fp8": "qwen",
}
DEFAULT_MODELS = (
    "gemini-3.5-flash",
    "gemini-3.5-flash-lite",
)
GEMINI_BASE_ENV = "AI_GATEWAY_GEMINI_BASE"
QWEN_BASE_ENV = "AI_GATEWAY_QWEN_BASE"
PROMPT_SHA256 = "fd119108d3ef4dbf2f88984511d9f903b7d4c98b032a95c327a21f713335e48e"
PARSER_VERSION = "pa_v149_json_repair_v0"
SCREEN_RUN_ID = "modern_screen_v1"
HARD_CAP = 20_000
QWEN_WARMUP_MAX_ATTEMPTS = 81
QWEN_WARMUP_INTERVAL_SECONDS = 15
QWEN_MAX_DIMENSION = 1280
QWEN_JPEG_QUALITY = 85
GEMINI_ROUTE_VERSION = "gemini_l1_native_inline_jpeg95_minimal4096_v2"
QWEN_ROUTE_VERSION = "qwen_l3_openai_inline_jpeg85_max1280_v1"
GENERATION_PARAMS = {
    "gemini": {
        "temperature": 0,
        "candidateCount": 1,
        "maxOutputTokens": 4096,
        "thinkingConfig": {"thinkingLevel": "MINIMAL"},
    },
    "qwen": {
        "temperature": 0,
        "max_tokens": 2048,
        "enable_thinking": False,
        "chat_template": "qwen_no_think_v1",
    },
}


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve_native_path(value: str | os.PathLike[str]) -> Path:
    raw = str(value)
    if os.name == "nt" and raw.startswith("/mnt/") and len(raw) > 6:
        return Path(f"{raw[5].upper()}:/{raw[7:]}")
    return Path(raw)


def load_yaml(path: Path) -> dict[str, Any]:
    import yaml

    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"local manifest must be a mapping: {path}")
    return data


def nested(data: dict[str, Any], *keys: str) -> Any:
    current: Any = data
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return None
        current = current[key]
    return current


def gateway_base(env_name: str) -> str:
    value = os.environ.get(env_name)
    if not value:
        raise RuntimeError(f"{env_name} is not present")
    value = value.strip().strip('"').strip("'").rstrip("/")
    if not value.startswith(("http://", "https://")):
        raise RuntimeError(f"{env_name} must be an HTTP(S) URL")
    return value


class LedgerStore:
    """Thread-safe append-only ledger using the package's validators."""

    def __init__(self, path: Path, accounting_paths: tuple[Path, ...] = ()):
        self.path = path
        main_path = path.resolve()
        self.accounting_paths = tuple(candidate.resolve() for candidate in accounting_paths if candidate.resolve() != main_path)
        self.lock = threading.RLock()
        self.records = read_ledger(path)
        validate_history(self.records)
        self.latest_by_key: dict[tuple[str, str, str, int], dict[str, Any]] = {}
        self.max_attempt_by_identity: dict[tuple[tuple[str, str, str, int], str], tuple[int, int]] = {}
        for record in self.records:
            key = (record["doc_id"], record["model_id"], record["transform_id"], record["sample_index"])
            self.latest_by_key[key] = record
            identity = (key, str(record["request_fingerprint"]))
            self.max_attempt_by_identity[identity] = (
                max(self.max_attempt_by_identity.get(identity, (0, 0))[0], int(record["attempt_count"])),
                max(self.max_attempt_by_identity.get(identity, (0, 0))[1], int(record["retry_count"])),
            )
        self.accounting_latest_by_identity: dict[
            tuple[tuple[str, str, str, int], str], dict[str, Any]
        ] = {}
        self.provider_attempts = sum(1 for record in self.records if record["status"] == "submitted")
        self.accounted_provider_attempts: dict[Path, int] = {}
        for accounting_path in self.accounting_paths:
            if not accounting_path.exists():
                continue
            accounting_records = read_ledger(accounting_path)
            validate_history(accounting_records)
            count = sum(1 for record in accounting_records if record["status"] == "submitted")
            self.accounted_provider_attempts[accounting_path] = count
            self.provider_attempts += count
            for record in accounting_records:
                key = (record["doc_id"], record["model_id"], record["transform_id"], record["sample_index"])
                if key not in self.latest_by_key:
                    identity = (key, str(record["request_fingerprint"]))
                    prior_max = self.max_attempt_by_identity.get(identity, (0, 0))
                    self.max_attempt_by_identity[identity] = (
                        max(prior_max[0], int(record["attempt_count"])),
                        max(prior_max[1], int(record["retry_count"])),
                    )
                    self.accounting_latest_by_identity[identity] = record

    def latest(
        self,
        key: tuple[str, str, str, int],
        request_fingerprint: str | None = None,
    ) -> dict[str, Any] | None:
        with self.lock:
            primary = self.latest_by_key.get(key)
            if primary is not None:
                return primary
            if request_fingerprint is not None:
                return self.accounting_latest_by_identity.get((key, request_fingerprint))
            candidates = [
                record
                for (candidate_key, _), record in self.accounting_latest_by_identity.items()
                if candidate_key == key
            ]
            if candidates:
                return candidates[-1]
            return None

    def append(self, record: dict[str, Any]) -> None:
        with self.lock:
            validate_record(record)
            key = (record["doc_id"], record["model_id"], record["transform_id"], record["sample_index"])
            prior = self.latest_by_key.get(key)
            if prior is not None:
                validate_history([prior, record])
            encoded = (canonical_json(record) + "\n").encode("utf-8")
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("ab") as stream:
                stream.write(encoded)
                stream.flush()
                os.fsync(stream.fileno())
            self.records.append(record)
            self.latest_by_key[key] = record
            identity = (key, str(record["request_fingerprint"]))
            prior_max = self.max_attempt_by_identity.get(identity, (0, 0))
            self.max_attempt_by_identity[identity] = (
                max(prior_max[0], int(record["attempt_count"])),
                max(prior_max[1], int(record["retry_count"])),
            )
            if record["status"] == "submitted":
                self.provider_attempts += 1

    def append_submitted_if_capacity(self, record: dict[str, Any]) -> None:
        """Durably append one submitted attempt while holding the cap lock."""
        with self.lock:
            if self.provider_attempts >= HARD_CAP:
                raise RuntimeError(f"hard provider-request cap exhausted: {HARD_CAP}")
            validate_record(record)
            key = (record["doc_id"], record["model_id"], record["transform_id"], record["sample_index"])
            prior = self.latest_by_key.get(key)
            if prior is not None:
                validate_history([prior, record])
            encoded = (canonical_json(record) + "\n").encode("utf-8")
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("ab") as stream:
                stream.write(encoded)
                stream.flush()
                os.fsync(stream.fileno())
            self.records.append(record)
            self.latest_by_key[key] = record
            identity = (key, str(record["request_fingerprint"]))
            prior_max = self.max_attempt_by_identity.get(identity, (0, 0))
            self.max_attempt_by_identity[identity] = (
                max(prior_max[0], int(record["attempt_count"])),
                max(prior_max[1], int(record["retry_count"])),
            )
            self.provider_attempts += 1

    def next_attempt_after_history(self, key: tuple[str, str, str, int], fingerprint: str) -> tuple[int, int]:
        attempt, retry_count = self.max_attempt_by_identity.get((key, fingerprint), (0, 0))
        return attempt + 1, retry_count + 1

    def reserve_provider_attempt(self) -> None:
        with self.lock:
            if self.provider_attempts >= HARD_CAP:
                raise RuntimeError(f"hard provider-request cap exhausted: {HARD_CAP}")


class ResultWriter:
    def __init__(self, root: Path):
        self.root = root
        self.lock = threading.Lock()

    def append(self, model_id: str, record: dict[str, Any]) -> None:
        path = self.root / model_id / "results.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        encoded = (canonical_json(record) + "\n").encode("utf-8")
        with self.lock:
            with path.open("ab") as stream:
                stream.write(encoded)
                stream.flush()
                os.fsync(stream.fileno())


class FailureCounter:
    def __init__(self):
        self.lock = threading.Lock()
        self.consecutive = 0
        self.total_failures = 0

    def failure(self) -> int:
        with self.lock:
            self.consecutive += 1
            self.total_failures += 1
            return self.consecutive

    def success(self) -> None:
        with self.lock:
            self.consecutive = 0


def make_schema_hash() -> str:
    schema = {"parser_version": PARSER_VERSION, "required_fields": list(PA_V149_REQUIRED_FIELDS)}
    return sha256_bytes(canonical_json(schema).encode("utf-8"))


def load_render_rows(path: Path, *, full: bool = False) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    required = {"doc_id", "view_id", "transform_id", "source_image_sha256", "rendered_image_sha256", "rendered_relative_filename", "status"}
    if not rows or not required.issubset(rows[0]):
        raise ValueError(f"render manifest missing required columns: {sorted(required)}")
    if any(row["status"] != "rendered" for row in rows):
        raise ValueError("render manifest contains a non-rendered row")
    if full:
        expected_views = {"U0", "U1", "U2", "P0", "P1", "P2", "G0", "G1", "G2"}
        keys = {(row["doc_id"], row["view_id"]) for row in rows}
        if len(rows) != 622 * len(expected_views) or len(keys) != len(rows):
            raise ValueError(
                f"full render manifest must contain 622*9 unique document-view rows; found {len(rows)} rows"
            )
        if {row["view_id"] for row in rows} != expected_views or len({row["doc_id"] for row in rows}) != 622:
            raise ValueError("full render manifest must cover exactly 622 documents and views U0-U2/P0-P2/G0-G2")
    return rows


def model_transport(model_id: str) -> tuple[str, str]:
    family = MODELS[model_id]
    if family == "gemini":
        return GEMINI_ROUTE_VERSION, "image/jpeg"
    return QWEN_ROUTE_VERSION, "image/jpeg"


def qwen_payload_bytes(rendered_path: Path) -> bytes:
    with Image.open(rendered_path) as image:
        image = image.convert("RGB")
        width, height = image.size
        if max(width, height) > QWEN_MAX_DIMENSION:
            scale = QWEN_MAX_DIMENSION / max(width, height)
            resampling = getattr(Image, "Resampling", Image).LANCZOS
            image = image.resize((max(1, round(width * scale)), max(1, round(height * scale))), resampling)
        output = io.BytesIO()
        image.save(output, format="JPEG", quality=QWEN_JPEG_QUALITY)
        return output.getvalue()


def transport_bytes(model_id: str, rendered_path: Path) -> bytes:
    if MODELS[model_id] == "gemini":
        return rendered_path.read_bytes()
    return qwen_payload_bytes(rendered_path)


def extract_gemini(body: dict[str, Any]) -> tuple[str, str | None, dict[str, Any]]:
    candidates = body.get("candidates") or []
    parts = ((candidates[0] if candidates else {}).get("content") or {}).get("parts") or []
    text = "".join(part.get("text", "") for part in parts if isinstance(part, dict))
    returned = body.get("modelVersion") or body.get("model") or body.get("model_version")
    return text, returned, body.get("usageMetadata") or {}


def extract_qwen(body: dict[str, Any]) -> tuple[str, str | None, dict[str, Any]]:
    choices = body.get("choices") or []
    message = (choices[0] if choices else {}).get("message") or {}
    content = message.get("content", "")
    if isinstance(content, list):
        text = "".join(item.get("text", "") for item in content if isinstance(item, dict))
    else:
        text = str(content)
    returned = body.get("model") or body.get("modelVersion") or body.get("model_version")
    return text, returned, body.get("usage") or {}


def normalize_returned_model(value: str | None) -> str | None:
    if value is None:
        return None
    value = str(value)
    for prefix in ("models/", "publishers/google/models/"):
        if value.startswith(prefix):
            value = value[len(prefix) :]
    return value


def provider_payload(
    model_id: str,
    prompt: str,
    image_bytes: bytes,
    *,
    gemini_key_env: str = "AI_GATEWAY_KEY",
) -> tuple[str, dict[str, str], dict[str, Any]]:
    family = MODELS[model_id]
    encoded = base64.b64encode(image_bytes).decode("ascii")
    if family == "gemini":
        url = f"{gateway_base(GEMINI_BASE_ENV)}/v1beta/models/{model_id}:generateContent"
        key = os.environ.get(gemini_key_env)
        if not key:
            raise RuntimeError(f"{gemini_key_env} is not present")
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": key,
            "Host": "generativelanguage.googleapis.com",
            "Ancestry-ClientPath": "ds-llm-v1",
            "Accept-Encoding": "identity",
        }
        payload = {
            "contents": [{"parts": [{"text": prompt}, {"inline_data": {"mime_type": "image/jpeg", "data": encoded}}]}],
            "generationConfig": GENERATION_PARAMS[family],
        }
        return url, headers, payload
    key = os.environ.get("AI_GATEWAY_KEY_PROD_L3")
    if not key:
        raise RuntimeError("AI_GATEWAY_KEY_PROD_L3 is not present")
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {key}"}
    payload = {
        "model": model_id,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded}"}},
                {"type": "text", "text": prompt + "\n/no_think"},
            ],
        }],
        "temperature": 0,
        "max_tokens": 2048,
        "extra_body": {"chat_template_kwargs": {"enable_thinking": False}},
    }
    return f"{gateway_base(QWEN_BASE_ENV)}/chat/completions", headers, payload


def base_record(task: dict[str, Any], descriptor: dict[str, Any], status: str, *, attempt: int, retry_count: int) -> dict[str, Any]:
    return {
        "schema_version": LEDGER_SCHEMA_VERSION,
        "doc_id": task["doc_id"],
        "model_id": task["model_id"],
        "transform_id": task["transform_id"],
        "sample_index": int(task["sample_index"]),
        "request_fingerprint": request_fingerprint(descriptor),
        "prompt_hash": descriptor["prompt_hash"],
        "status": status,
        "attempt_count": attempt,
        "retry_count": retry_count,
        "source_image_hash": descriptor["source_image_hash"],
        "rendered_image_hash": descriptor["rendered_image_hash"],
        "payload_hash": descriptor["payload_hash"],
        "provider": "ancestry_ai_gateway",
        "route_transport_version": descriptor["route_transport_version"],
        "screen_run_id": SCREEN_RUN_ID,
        "updated_timestamp_utc": now_utc(),
    }


def run_one(
    task: dict[str, Any],
    *,
    prompt: str,
    schema_hash: str,
    render_root: Path,
    raw_root: Path,
    store: LedgerStore,
    result_writer: ResultWriter,
    failure_counter: FailureCounter,
    stop_event: threading.Event,
    require_returned_model: bool,
    gemini_key_env: str,
    allow_capacity_retry: bool = False,
    allow_route_repair: bool = False,
) -> dict[str, Any]:
    model_id = task["model_id"]
    rendered_path = render_root / task["rendered_relative_filename"]
    if not rendered_path.exists():
        raise FileNotFoundError(f"rendered image missing: {rendered_path}")
    actual_rendered_hash = sha256_file(rendered_path)
    if actual_rendered_hash.lower() != str(task["rendered_image_sha256"]).lower():
        raise RuntimeError(
            f"rendered image hash mismatch for {task['doc_id']} {task['view_id']}: "
            f"manifest={task['rendered_image_sha256']} actual={actual_rendered_hash}"
        )
    image_bytes = transport_bytes(model_id, rendered_path)
    route_version, _ = model_transport(model_id)
    descriptor = {
        "model_id": model_id,
        "prompt_hash": PROMPT_SHA256,
        "schema_hash": schema_hash,
        "source_image_hash": task["source_image_sha256"],
        "rendered_image_hash": actual_rendered_hash,
        "payload_hash": sha256_bytes(image_bytes),
        "transform_id": task["transform_id"],
        "sample_index": int(task["sample_index"]),
        "generation_params": GENERATION_PARAMS[MODELS[model_id]],
        "route_transport_version": route_version,
        "gemini_key_env": gemini_key_env if MODELS[model_id] == "gemini" else None,
    }
    fingerprint = request_fingerprint(descriptor)
    key = (task["doc_id"], model_id, task["transform_id"], int(task["sample_index"]))
    prior = store.latest(key, request_fingerprint=fingerprint)
    capacity_retry = False
    if prior is not None and prior["status"] in {"capacity_failure", "non_retryable_failure", "network_failure", "failed"} and (allow_capacity_retry or allow_route_repair):
        attempt, retry_count = store.next_attempt_after_history(key, fingerprint)
        capacity_retry = True
        prior = None
    if prior is not None:
        if prior["request_fingerprint"] != fingerprint:
            raise RuntimeError(f"ledger fingerprint mismatch for {key}")
        if prior["status"] in {"ok", "parse_fail_kept"}:
            return {"status": "skipped_terminal", "model_id": model_id, "doc_id": task["doc_id"]}
        if prior["status"] in {"submitted", "ambiguous_submission", "reconciling", "capacity_failure", "non_retryable_failure", "failed"}:
            raise RuntimeError(f"ledger requires manual reconciliation for {key}: {prior['status']}")
        attempt = int(prior["attempt_count"]) + 1
        retry_count = int(prior["retry_count"])
    else:
        if not capacity_retry:
            attempt = 1
            retry_count = 0
            store.append(base_record(task, descriptor, "reserved", attempt=attempt - 1, retry_count=retry_count))

    while True:
        if stop_event.is_set():
            return {"status": "stopped_before_submit", "model_id": model_id, "doc_id": task["doc_id"]}
        submitted = base_record(task, descriptor, "submitted", attempt=attempt, retry_count=retry_count)
        submitted["request_timestamp_utc"] = now_utc()
        store.append_submitted_if_capacity(submitted)
        started = time.perf_counter()
        raw_ref = f"{model_id}/{task['doc_id']}__{task['view_id']}__attempt_{attempt}.json"
        raw_path = raw_root / raw_ref
        raw_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            url, headers, payload = provider_payload(
                model_id,
                prompt,
                image_bytes,
                gemini_key_env=gemini_key_env,
            )
            with httpx.Client(verify=False, timeout=180) as client:
                response = client.post(url, headers=headers, json=payload)
            elapsed = time.perf_counter() - started
            raw_bytes = response.content
            raw_path.write_bytes(raw_bytes)
        except httpx.ReadTimeout as exc:
            elapsed = time.perf_counter() - started
            consecutive = failure_counter.failure()
            event = base_record(task, descriptor, "ambiguous_submission", attempt=attempt, retry_count=retry_count)
            event.update({"response_timestamp_utc": now_utc(), "latency_seconds": elapsed, "error_class": type(exc).__name__, "raw_response_ref": raw_ref})
            store.append(event)
            stop_event.set()
            raise RuntimeError(f"ambiguous provider submission for {key}; consecutive_failures={consecutive}") from exc
        except httpx.RequestError as exc:
            elapsed = time.perf_counter() - started
            consecutive = failure_counter.failure()
            event = base_record(task, descriptor, "network_failure", attempt=attempt, retry_count=retry_count)
            event.update({"response_timestamp_utc": now_utc(), "latency_seconds": elapsed, "error_class": type(exc).__name__, "raw_response_ref": raw_ref})
            store.append(event)
            if consecutive >= 5:
                stop_event.set()
                raise RuntimeError(f"five consecutive network failures; stopped at {key}") from exc
            if retry_count >= 1:
                failed = base_record(task, descriptor, "failed", attempt=attempt, retry_count=retry_count)
                failed.update({"response_timestamp_utc": now_utc(), "latency_seconds": elapsed, "error_class": type(exc).__name__})
                store.append(failed)
                return {"status": "failed", "model_id": model_id, "doc_id": task["doc_id"]}
            retry_count += 1
            attempt += 1
            store.append(base_record(task, descriptor, "reserved", attempt=attempt - 1, retry_count=retry_count))
            continue
        except Exception:
            stop_event.set()
            raise

        failure_counter.success()
        if response.status_code != 200:
            text = response.text[:500]
            if response.status_code == 429 or "capacity" in text.lower():
                event = base_record(task, descriptor, "capacity_failure", attempt=attempt, retry_count=retry_count)
                event.update({"response_timestamp_utc": now_utc(), "latency_seconds": elapsed, "http_status": response.status_code, "raw_response_ref": raw_ref})
                store.append(event)
                stop_event.set()
                raise RuntimeError(f"provider capacity failure at {key}; response saved to {raw_ref}")
            if response.status_code >= 500 and retry_count < 1:
                consecutive = failure_counter.failure()
                event = base_record(task, descriptor, "network_failure", attempt=attempt, retry_count=retry_count)
                event.update({"response_timestamp_utc": now_utc(), "latency_seconds": elapsed, "http_status": response.status_code, "raw_response_ref": raw_ref})
                store.append(event)
                if consecutive >= 5:
                    stop_event.set()
                    raise RuntimeError(f"five consecutive HTTP failures; stopped at {key}")
                retry_count += 1
                attempt += 1
                store.append(base_record(task, descriptor, "reserved", attempt=attempt - 1, retry_count=retry_count))
                continue
            event = base_record(task, descriptor, "non_retryable_failure", attempt=attempt, retry_count=retry_count)
            event.update({"response_timestamp_utc": now_utc(), "latency_seconds": elapsed, "http_status": response.status_code, "raw_response_ref": raw_ref})
            store.append(event)
            stop_event.set()
            raise RuntimeError(f"non-retryable provider status {response.status_code} at {key}")

        try:
            body = response.json()
        except ValueError as exc:
            event = base_record(task, descriptor, "parse_fail_kept", attempt=attempt, retry_count=retry_count)
            event.update({"response_timestamp_utc": now_utc(), "latency_seconds": elapsed, "raw_response_ref": raw_ref, "parser_version": PARSER_VERSION, "parse_failure_reason": "provider_body_not_json"})
            store.append(event)
            result = {
                **task,
                "model_id": model_id,
                "status": "parse_fail_kept",
                "raw_response_ref": raw_ref,
                "parser_failure_reason": "provider_body_not_json",
                "attempt_count": attempt,
                "retry_count": retry_count,
                "screen_run_id": SCREEN_RUN_ID,
                "parser_version": PARSER_VERSION,
                "prompt_hash": PROMPT_SHA256,
                "schema_hash": schema_hash,
                "request_fingerprint": fingerprint,
                "source_image_hash": descriptor["source_image_hash"],
                "rendered_image_hash": descriptor["rendered_image_hash"],
                "payload_hash": descriptor["payload_hash"],
                "route_transport_version": descriptor["route_transport_version"],
                "gemini_key_env": descriptor["gemini_key_env"],
                "generation_params": descriptor["generation_params"],
            }
            result_writer.append(model_id, result)
            return result
        text, returned_model, usage = extract_gemini(body) if MODELS[model_id] == "gemini" else extract_qwen(body)
        normalized_returned = normalize_returned_model(returned_model)
        if normalized_returned is not None and normalized_returned != model_id:
            event = base_record(task, descriptor, "non_retryable_failure", attempt=attempt, retry_count=retry_count)
            event.update({"response_timestamp_utc": now_utc(), "latency_seconds": elapsed, "raw_response_ref": raw_ref, "returned_model_id": normalized_returned, "error_class": "returned_model_mismatch"})
            store.append(event)
            stop_event.set()
            raise RuntimeError(f"returned model mismatch at {key}: {normalized_returned!r} != {model_id!r}")
        if require_returned_model and normalized_returned is None:
            event = base_record(task, descriptor, "non_retryable_failure", attempt=attempt, retry_count=retry_count)
            event.update({"response_timestamp_utc": now_utc(), "latency_seconds": elapsed, "raw_response_ref": raw_ref, "error_class": "returned_model_id_missing"})
            store.append(event)
            stop_event.set()
            raise RuntimeError(f"returned model ID missing at {key}")
        parsed = parse_response_json(text, api_status="200")
        if hasattr(parsed, "values"):
            status = "ok"
            parser_failure = None
            parsed_payload = {"values": parsed.values, "confidences": parsed.confidences, "repair_path": list(parsed.repair_path)}
        else:
            status = "parse_fail_kept"
            parser_failure = {"reason": parsed.reason.value, "detail": parsed.detail}
            parsed_payload = None
        event = base_record(task, descriptor, status, attempt=attempt, retry_count=retry_count)
        event.update({"response_timestamp_utc": now_utc(), "latency_seconds": elapsed, "raw_response_ref": raw_ref, "parser_version": PARSER_VERSION, "usage": usage})
        if normalized_returned is not None:
            event["returned_model_id"] = normalized_returned
        store.append(event)
        result = {
            **task,
            "model_id": model_id,
            "status": status,
            "raw_response_ref": raw_ref,
            "returned_model_id": normalized_returned,
            "usage": usage,
            "latency_seconds": elapsed,
            "attempt_count": attempt,
            "retry_count": retry_count,
            "parsed": parsed_payload,
            "parser_failure": parser_failure,
            "screen_run_id": SCREEN_RUN_ID,
            "parser_version": PARSER_VERSION,
            "prompt_hash": PROMPT_SHA256,
            "schema_hash": schema_hash,
            "request_fingerprint": fingerprint,
            "source_image_hash": descriptor["source_image_hash"],
            "rendered_image_hash": descriptor["rendered_image_hash"],
            "payload_hash": descriptor["payload_hash"],
            "route_transport_version": descriptor["route_transport_version"],
            "gemini_key_env": descriptor["gemini_key_env"],
            "generation_params": descriptor["generation_params"],
        }
        result_writer.append(model_id, result)
        return result


def warmup_qwen(prompt: str, store: LedgerStore, raw_root: Path) -> dict[str, Any]:
    """Serialized Qwen warmup; no keepalive thread is started."""
    op_task = {
        "doc_id": "__operational__",
        "model_id": "sagemaker-qwen3-vl-8b-instruct-fp8",
        "transform_id": "qwen_warmup.0",
        "sample_index": "0",
        "view_id": "warmup",
        "source_image_sha256": "operational-no-image",
        "rendered_image_sha256": "operational-no-image",
        "rendered_relative_filename": "",
    }
    descriptor = {
        "model_id": op_task["model_id"], "prompt_hash": PROMPT_SHA256, "schema_hash": make_schema_hash(),
        "source_image_hash": "operational-no-image", "rendered_image_hash": "operational-no-image",
        "payload_hash": sha256_bytes(b"ok /no_think"), "transform_id": op_task["transform_id"], "sample_index": 0,
        "generation_params": {"temperature": 0, "max_tokens": 5, "enable_thinking": False},
        "route_transport_version": QWEN_ROUTE_VERSION + ":warmup",
    }
    key = (op_task["doc_id"], op_task["model_id"], op_task["transform_id"], 0)
    prior = store.latest(key)
    if prior is not None:
        if prior["status"] == "ok":
            return {"status": "skipped_terminal"}
        if prior["status"] in {"non_retryable_failure", "capacity_failure", "ambiguous_submission", "reconciling"}:
            raise RuntimeError(f"Qwen warmup is already terminal and requires route repair: {prior['status']}")
    for attempt in range(1, QWEN_WARMUP_MAX_ATTEMPTS + 1):
        if store.latest(key) is None:
            store.append(base_record(op_task, descriptor, "reserved", attempt=0, retry_count=0))
        store.append_submitted_if_capacity(base_record(op_task, descriptor, "submitted", attempt=attempt, retry_count=0))
        started = time.perf_counter()
        raw_ref = f"sagemaker-qwen3-vl-8b-instruct-fp8/__operational__warmup__attempt_{attempt}.json"
        try:
            key_value = os.environ.get("AI_GATEWAY_KEY_PROD_L3")
            if not key_value:
                raise RuntimeError("AI_GATEWAY_KEY_PROD_L3 is not present")
            headers = {"Content-Type": "application/json", "Authorization": f"Bearer {key_value}"}
            payload = {"model": op_task["model_id"], "messages": [{"role": "user", "content": "ok /no_think"}], "temperature": 0, "max_tokens": 5, "extra_body": {"chat_template_kwargs": {"enable_thinking": False}}}
            with httpx.Client(verify=False, timeout=30) as client:
                response = client.post(f"{gateway_base(QWEN_BASE_ENV)}/chat/completions", headers=headers, json=payload)
            raw_root.joinpath(raw_ref).parent.mkdir(parents=True, exist_ok=True)
            raw_root.joinpath(raw_ref).write_bytes(response.content)
            elapsed = time.perf_counter() - started
            if response.status_code == 200:
                event = base_record(op_task, descriptor, "ok", attempt=attempt, retry_count=0)
                event.update({"response_timestamp_utc": now_utc(), "latency_seconds": elapsed, "raw_response_ref": raw_ref, "returned_model_id": op_task["model_id"], "provider": "ancestry_ai_gateway"})
                store.append(event)
                return {"status": "ok", "attempts": attempt}
            if response.status_code == 429 or "capacity" in response.text.lower():
                event = base_record(op_task, descriptor, "capacity_failure", attempt=attempt, retry_count=0)
                event.update({"response_timestamp_utc": now_utc(), "latency_seconds": elapsed, "raw_response_ref": raw_ref, "http_status": response.status_code})
                store.append(event)
                raise RuntimeError("Qwen warmup capacity failure")
            if response.status_code >= 400:
                event = base_record(op_task, descriptor, "non_retryable_failure", attempt=attempt, retry_count=0)
                event.update({"response_timestamp_utc": now_utc(), "latency_seconds": elapsed, "raw_response_ref": raw_ref, "http_status": response.status_code, "error_class": "qwen_endpoint_or_route_failure"})
                store.append(event)
                raise RuntimeError(f"Qwen warmup non-retryable HTTP status {response.status_code}")
        except httpx.RequestError:
            elapsed = time.perf_counter() - started
            event = base_record(op_task, descriptor, "network_failure", attempt=attempt, retry_count=0)
            event.update({"response_timestamp_utc": now_utc(), "latency_seconds": elapsed, "raw_response_ref": raw_ref})
            store.append(event)
        if attempt < QWEN_WARMUP_MAX_ATTEMPTS:
            time.sleep(QWEN_WARMUP_INTERVAL_SECONDS)
    raise RuntimeError(f"Qwen warmup failed after {QWEN_WARMUP_MAX_ATTEMPTS} attempts")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--smoke", action="store_true")
    mode.add_argument("--full", action="store_true")
    parser.add_argument("--authorize-live", action="store_true")
    parser.add_argument("--render-manifest", required=True, type=Path)
    parser.add_argument("--local-manifest", default=Path("config/data_manifest.local.yaml"), type=Path)
    parser.add_argument("--ledger", default=Path("local_agent/runtime/modern_request_ledger.jsonl"), type=Path)
    parser.add_argument("--accounting-ledger", action="append", default=[], type=Path, help="additional ledger(s) counted toward the shared hard cap")
    parser.add_argument("--raw-root", type=Path, default=None)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--allow-capacity-retry", action="store_true")
    parser.add_argument("--allow-route-repair", action="store_true")
    parser.add_argument("--models", default=",".join(DEFAULT_MODELS), help="comma-separated exact model IDs")
    parser.add_argument("--gemini-key-env", default="AI_GATEWAY_KEY", help="environment variable holding the Gemini gateway key")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.workers <= 0:
        raise ValueError("--workers must be positive")
    requested_models = tuple(value.strip() for value in args.models.split(",") if value.strip())
    if any(model not in MODELS for model in requested_models):
        raise ValueError(f"unknown model; allowed={sorted(MODELS)}")
    if not args.dry_run and not args.authorize_live:
        raise SystemExit("Refusing provider calls without --authorize-live")

    local = load_yaml(args.local_manifest)
    prompt_value = nested(local, "sources", "prompts", "pa_v149_confidence")
    if not prompt_value:
        raise ValueError("local manifest has no sources.prompts.pa_v149_confidence")
    prompt_path = resolve_native_path(prompt_value)
    prompt_bytes = prompt_path.read_bytes()
    prompt_sha = sha256_bytes(prompt_bytes)
    if prompt_sha.lower() != PROMPT_SHA256:
        raise ValueError(f"prompt SHA mismatch: {prompt_path}")
    prompt = prompt_bytes.decode("utf-8")
    render_manifest = args.render_manifest.resolve()
    render_rows = load_render_rows(render_manifest, full=args.full)
    render_root = render_manifest.parent
    raw_root = args.raw_root or resolve_native_path(nested(local, "sources", "scratch", "response_root") or "local_agent/runtime/modern_responses")
    raw_root.mkdir(parents=True, exist_ok=True)
    tasks: list[dict[str, Any]] = []
    selected_rows = render_rows
    if args.smoke:
        first_docs = []
        for row in render_rows:
            if row["doc_id"] not in first_docs:
                first_docs.append(row["doc_id"])
            if len(first_docs) == 3:
                break
        selected_rows = [row for row in render_rows if row["doc_id"] in first_docs and row["view_id"] == "U0"]
    for row in selected_rows:
        for model_id in requested_models:
            task = dict(row)
            task["model_id"] = model_id
            tasks.append(task)
    expected = len(selected_rows) * len(requested_models)
    if len(tasks) != expected:
        raise RuntimeError(f"task construction mismatch: {len(tasks)} != {expected}")
    if args.dry_run:
        print(json.dumps({"mode": "smoke" if args.smoke else "full", "rows": len(selected_rows), "models": list(requested_models), "provider_requests": len(tasks), "render_root": str(render_root)}, sort_keys=True))
        return 0

    families = {MODELS[model_id] for model_id in requested_models}
    if "gemini" in families:
        gateway_base(GEMINI_BASE_ENV)
        if not os.environ.get(args.gemini_key_env):
            raise RuntimeError(f"{args.gemini_key_env} is not present")
    if "qwen" in families:
        gateway_base(QWEN_BASE_ENV)
        if not os.environ.get("AI_GATEWAY_KEY_PROD_L3"):
            raise RuntimeError("AI_GATEWAY_KEY_PROD_L3 is not present")

    auth = {
        "authorized_at_utc": now_utc(),
        "scope": "PA modern transfer screen requested by project owner",
        "mode": "smoke" if args.smoke else "full",
        "models": list(requested_models),
        "planned_scored_requests": len(tasks),
        "hard_cap": HARD_CAP,
        "no_gemini_2_0_calls": True,
    }
    auth_path = Path("local_agent/runtime/live_authorization.json")
    auth_path.parent.mkdir(parents=True, exist_ok=True)
    auth_path.write_text(canonical_json(auth) + "\n", encoding="utf-8")
    store = LedgerStore(args.ledger, tuple(args.accounting_ledger))
    result_writer = ResultWriter(raw_root / "normalized")
    failure_counter = FailureCounter()
    stop_event = threading.Event()

    if "sagemaker-qwen3-vl-8b-instruct-fp8" in requested_models:
        print("Qwen warmup: serialized, no concurrent keepalive", flush=True)
        warmup_result = warmup_qwen(prompt, store, raw_root)
        print(f"Qwen warmup result: {warmup_result}", flush=True)

    print(f"Starting {len(tasks)} provider requests with workers={args.workers}; ledger_attempts={store.provider_attempts}", flush=True)
    results: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=min(args.workers, len(tasks))) as executor:
        futures = [executor.submit(run_one, task, prompt=prompt, schema_hash=make_schema_hash(), render_root=render_root, raw_root=raw_root, store=store, result_writer=result_writer, failure_counter=failure_counter, stop_event=stop_event, require_returned_model=args.smoke, gemini_key_env=args.gemini_key_env, allow_capacity_retry=args.allow_capacity_retry, allow_route_repair=args.allow_route_repair) for task in tasks]
        for index, future in enumerate(as_completed(futures), start=1):
            result = future.result()
            results.append(result)
            if index == 1 or index % 25 == 0 or index == len(futures):
                print(f"completed {index}/{len(futures)}; provider_attempts={store.provider_attempts}; status={result.get('status')}", flush=True)

    receipt = {
        "schema_version": 1,
        "status": "complete" if not stop_event.is_set() else "stopped",
        "mode": "smoke" if args.smoke else "full",
        "run_id": SCREEN_RUN_ID,
        "models": list(requested_models),
        "gemini_key_env": args.gemini_key_env,
        "render_manifest": str(render_manifest),
        "render_rows": len(selected_rows),
        "planned_scored_requests": len(tasks),
        "provider_attempts_in_ledger": store.provider_attempts,
        "accounting_ledgers": [str(path) for path in args.accounting_ledger],
        "hard_cap": HARD_CAP,
        "failure_counter": {"total": failure_counter.total_failures, "consecutive_at_end": failure_counter.consecutive},
        "ledger": str(args.ledger),
        "raw_root": str(raw_root),
        "prompt_sha256": PROMPT_SHA256,
        "schema_hash": make_schema_hash(),
        "parser_version": PARSER_VERSION,
        "no_gemini_2_0_calls": True,
        "result_counts": {status: sum(1 for result in results if result.get("status") == status) for status in sorted({result.get("status") for result in results})},
    }
    receipt_path = Path("local_agent/runtime") / f"modern_screen_{'smoke' if args.smoke else 'full'}_receipt.json"
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(canonical_json(receipt) + "\n", encoding="utf-8")
    print(json.dumps(receipt, sort_keys=True), flush=True)
    return 0 if receipt["status"] == "complete" else 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"run_modern_screen: ERROR: {exc}", file=sys.stderr)
        raise
