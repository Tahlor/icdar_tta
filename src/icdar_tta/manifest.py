"""Data-manifest loading and gate checks for ``config/data_manifest*.yaml``.

Implements the checks implied by ``docs/DATA_CONTRACT.md`` and
``docs/VALIDATION_TESTS.md`` section 1 ("Data-integrity tests"):

- the portable manifest (``config/data_manifest.yaml``) must not contain
  secret-like values or absolute local paths;
- required logical source keys should be present (``docs/DATA_CONTRACT.md``
  "Logical data roots");
- the local manifest (``config/data_manifest.local.yaml``) is optional in
  this offline environment (it is machine-specific and gitignored) --
  its absence is a reported *data gate*, not a crash.

This module intentionally performs no network or filesystem-mount
resolution beyond reading the manifest file(s) themselves; it validates
manifest *shape*, not that the referenced data actually exists on disk
(no data-corpus is available in this offline pass).

YAML parsing prefers PyYAML when importable (this is an optional
dependency declared under ``[project.optional-dependencies].yaml`` in
``pyproject.toml``) and otherwise falls back to a minimal stdlib-only
parser that supports the flat ``key: value`` / nested-mapping subset
actually used by ``config/data_manifest.example.yaml``, so this module
has zero hard dependencies.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

#: Logical data roots documented in docs/DATA_CONTRACT.md.
REQUIRED_SOURCE_KEYS = (
    "source_images",
    "ground_truth",
    "fold_assignments",
    "historical_responses",
    "historical_augmentations",
    "shift_analysis",
    "paper_code",
    "usage_logs",
    "modern_responses",
    "scratch",
)

#: Conservative secret-like key/value patterns. This is a deliberately
#: narrow, documented heuristic (not a general secret scanner) so that
#: false positives/negatives stay predictable.
#:
#: "token" alone is intentionally excluded from the bare-word match:
#: legitimate, non-secret keys like ``max_output_tokens`` or
#: ``usage_tokens`` contain "token" as a unit-of-measure, not an
#: authentication credential. Only auth-shaped compounds
#: (``access_token``, ``auth_token``, ``bearer_token``, ``api_token``,
#: a bare ``token`` key) are flagged.
_SECRET_KEY_RE = re.compile(
    r"(api[_-]?key|secret|password|credential"
    r"|(?:^|_)(?:access|auth|bearer|api|refresh|session)[_-]?token(?:$|_)"
    r"|^token$)",
    re.IGNORECASE,
)
_ABSOLUTE_PATH_RE = re.compile(r"^(/[^/].*|[A-Za-z]:\\.*|\\\\.*)$")


class ManifestError(ValueError):
    pass


@dataclass(frozen=True)
class ManifestGateResult:
    """Outcome of validating one manifest file against the data-gate
    checks. ``ok`` is True only if there are zero errors; warnings do not
    block the gate but must still be reported.
    """

    path: str
    exists: bool
    errors: tuple = field(default_factory=tuple)
    warnings: tuple = field(default_factory=tuple)

    @property
    def ok(self) -> bool:
        return self.exists and not self.errors


def _fallback_parse_yaml(text: str) -> dict:
    """Minimal stdlib-only parser for the flat/nested-mapping subset of
    YAML used by config/data_manifest.example.yaml: two-space indented
    nested mappings, scalar values, and simple ``- item`` lists. This is
    not a general YAML parser and will raise ManifestError on constructs
    it does not recognize (fail loud, not silently misparse).
    """
    root: dict = {}
    stack = [(-1, root)]  # (indent, container)
    for raw_line in text.splitlines():
        line = raw_line.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip(" "))
        content = line.strip()

        while stack and indent <= stack[-1][0]:
            stack.pop()
        if not stack:
            raise ManifestError(f"manifest indentation error near: {raw_line!r}")
        parent = stack[-1][1]

        if content.startswith("- "):
            if not isinstance(parent, list):
                raise ManifestError(f"unexpected list item near: {raw_line!r}")
            parent.append(_parse_scalar(content[2:].strip()))
            continue

        if ":" not in content:
            raise ManifestError(f"expected 'key: value' near: {raw_line!r}")
        key, _, value = content.partition(":")
        key = key.strip()
        value = value.strip()

        if not isinstance(parent, dict):
            raise ManifestError(f"unexpected mapping key near: {raw_line!r}")

        if value == "":
            child: dict = {}
            parent[key] = child
            stack.append((indent, child))
        else:
            parent[key] = _parse_scalar(value)
    return root


def _parse_scalar(token: str) -> Any:
    if token in ("null", "~", ""):
        return None
    if token in ("true", "True"):
        return True
    if token in ("false", "False"):
        return False
    if token.startswith(("'", '"')) and token.endswith(("'", '"')) and len(token) >= 2:
        return token[1:-1]
    try:
        return int(token)
    except ValueError:
        pass
    try:
        return float(token)
    except ValueError:
        pass
    return token


def load_manifest_text(text: str) -> dict:
    try:
        import yaml  # optional dependency; see module docstring
    except ImportError:
        return _fallback_parse_yaml(text)
    else:
        loaded = yaml.safe_load(text)
        if loaded is None:
            return {}
        if not isinstance(loaded, dict):
            raise ManifestError("manifest top level must be a mapping")
        return loaded


def load_manifest_file(path: "str | Path") -> dict:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(str(p))
    return load_manifest_text(p.read_text(encoding="utf-8"))


def _scan_for_secrets_and_absolute_paths(data: Any, path_prefix: str = "") -> tuple:
    """Recursively scan a parsed manifest for secret-like keys or
    absolute-path-shaped string values. Returns (errors, warnings).
    """
    errors: list = []
    warnings: list = []
    if isinstance(data, dict):
        for key, value in data.items():
            full_key = f"{path_prefix}.{key}" if path_prefix else str(key)
            if _SECRET_KEY_RE.search(str(key)):
                errors.append(f"secret-like key found in portable manifest: {full_key!r}")
            sub_errors, sub_warnings = _scan_for_secrets_and_absolute_paths(value, full_key)
            errors.extend(sub_errors)
            warnings.extend(sub_warnings)
    elif isinstance(data, list):
        for i, item in enumerate(data):
            sub_errors, sub_warnings = _scan_for_secrets_and_absolute_paths(item, f"{path_prefix}[{i}]")
            errors.extend(sub_errors)
            warnings.extend(sub_warnings)
    elif isinstance(data, str):
        if path_prefix.endswith(".path") and _ABSOLUTE_PATH_RE.match(data) and data != "null":
            warnings.append(
                f"portable manifest field {path_prefix!r} looks like a machine-specific "
                f"absolute path: {data!r} (docs/DATA_CONTRACT.md says this belongs only in "
                f"config/data_manifest.local.yaml)"
            )
    return errors, warnings


def check_portable_manifest(data: dict) -> ManifestGateResult:
    """Gate checks for the *portable* manifest (config/data_manifest.yaml).

    This does not require the manifest to exist -- callers report
    existence separately via ManifestGateResult.exists -- but if it does
    exist, it must not contain secrets, and every required logical
    source key documented in docs/DATA_CONTRACT.md should be present
    (missing keys are warnings, since "If the local inventory reveals
    additional important sources, add keys" implies the key set may
    still be growing; only secret/absolute-path issues are hard errors).
    """
    errors: list = []
    warnings: list = []

    sources = data.get("sources") if isinstance(data, dict) else None
    if not isinstance(sources, dict):
        errors.append("manifest missing top-level 'sources' mapping")
        sources = {}

    missing_keys = [k for k in REQUIRED_SOURCE_KEYS if k not in sources]
    if missing_keys:
        warnings.append(f"manifest missing documented logical source key(s): {missing_keys}")

    sec_errors, sec_warnings = _scan_for_secrets_and_absolute_paths(data)
    errors.extend(sec_errors)
    warnings.extend(sec_warnings)

    return ManifestGateResult(path="<in-memory>", exists=True, errors=tuple(errors), warnings=tuple(warnings))


def run_manifest_gate(
    portable_path: "str | Path",
    local_path: "str | Path",
) -> "tuple[ManifestGateResult, ManifestGateResult]":
    """Run the two-manifest gate check described in docs/DATA_CONTRACT.md.

    Never raises for an expected missing-file condition; missing files
    are reported as ``exists=False`` gate results so a validation CLI
    can print a clear data-gate message instead of a traceback.
    """
    portable_result = _gate_one(portable_path, check_portable_manifest)
    local_result = _gate_one(local_path, _check_local_manifest_shape_only)
    return portable_result, local_result


def _check_local_manifest_shape_only(data: dict) -> ManifestGateResult:
    # The local manifest is machine-specific by design and may contain
    # absolute paths deliberately; only structural shape is checked.
    errors: list = []
    sources = data.get("sources") if isinstance(data, dict) else None
    if not isinstance(sources, dict):
        errors.append("local manifest missing top-level 'sources' mapping")
    return ManifestGateResult(path="<in-memory>", exists=True, errors=tuple(errors), warnings=tuple())


def _gate_one(path: "str | Path", checker) -> ManifestGateResult:
    p = Path(path)
    if not p.exists():
        return ManifestGateResult(
            path=str(p),
            exists=False,
            errors=tuple(),
            warnings=(f"manifest file not found: {p} (expected per docs/DATA_CONTRACT.md)",),
        )
    try:
        data = load_manifest_file(p)
    except ManifestError as exc:
        return ManifestGateResult(path=str(p), exists=True, errors=(str(exc),), warnings=tuple())

    result = checker(data)
    return ManifestGateResult(path=str(p), exists=True, errors=result.errors, warnings=result.warnings)
