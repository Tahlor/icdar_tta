#!/usr/bin/env python3
"""Render and hash the frozen nine-view modern-model screen.

The script deliberately keeps rendered/private image bytes outside Git.  It
reads the portable source manifest and the ignored local manifest, applies the
historical 1,504-pixel resize, the recovered granular Pad implementation, and
the recovered handwriting-kernel Grid Warp implementation, then writes a
portable row-oriented render manifest beside the private images.

The historical Grid configuration used an unset NumPy random state.  The
modern transfer screen therefore uses a documented, stable per-document/view
seed.  This is a deterministic transfer renderer, not a claim that the
historical random pixels have been recovered.

Run with the bundled runtime and the ignored dependency directory on
``PYTHONPATH``.  For example, from PowerShell:

    $env:PYTHONPATH = "local_agent/runtime/python_deps;path/to/chat2rec_v1"
    python scripts/render_modern_views.py --limit 3 --output-dir path/to/private/rendered_views

The full run is resumable.  It never calls a provider.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Iterable

import cv2
import numpy as np


SOURCE_MANIFEST_FIELDS = (
    "doc_id",
    "relative_filename",
    "byte_size",
    "sha256",
    "source_role",
)
VIEW_ORDER = ("U0", "U1", "U2", "P0", "P1", "P2", "G0", "G1", "G2")
PAD_PARAMS = {
    "P0": {"pad_left": 16, "pad_right": 16, "pad_top": 16, "pad_bottom": 16},
    "P1": {"pad_left": 8, "pad_right": 24, "pad_top": 8, "pad_bottom": 24},
    "P2": {"pad_left": 28, "pad_right": 4, "pad_top": 28, "pad_bottom": 4},
}
GRID_IDS = {
    "G0": "dont_warp_text_and_lines_d003_r30_s10_std15",
    "G1": "warp_all_d003_r30_s10_std15",
    "G2": "warp_hw_only_dont_warp_text_and_lines_d003_r30_s10_std15",
}
GRID_CHANNELS = {
    "G0": {"do_not_warp_channels": [0, 1]},
    "G1": {},
    "G2": {"do_warp_channels": [2], "do_not_warp_channels": [0, 1]},
}
GRID_COMMON_PARAMS = {
    "prob": 1.0,
    "point_density": 0.003,
    "base_radius": 30.0,
    "boundary_safety": 1.0,
    "min_radius": 5.0,
    "warp_strength": 10.0,
    "noise_std": 1.5,
    "falloff_type": "gaussian",
    "region_based": True,
    "region_margin": 20,
    "min_influence": 0.01,
    "min_region_area": 100,
    "dilate_radius": 3,
    "min_component_size": 50,
    "target_scale": 1200,
    "auto_scale_params": True,
    "full_image_mode": False,
    "mask_suffix": ".tif",
}
RENDER_MANIFEST_FIELDS = (
    "doc_id",
    "view_id",
    "strategy",
    "transform_id",
    "sample_index",
    "source_relative_filename",
    "source_image_sha256",
    "mask_relative_filename",
    "mask_sha256",
    "transform_spec_json",
    "transform_spec_sha256",
    "seed",
    "rendered_relative_filename",
    "rendered_image_sha256",
    "width",
    "height",
    "channels",
    "codec",
    "codec_options",
    "renderer_sha256",
    "external_grid_renderer_sha256",
    "external_pad_renderer_sha256",
    "status",
)


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
    """Resolve a WSL-style local-manifest path on Windows when needed."""
    raw = str(value)
    if os.name == "nt":
        match = re.fullmatch(r"/mnt/([a-zA-Z])/(.*)", raw)
        if match:
            return Path(f"{match.group(1).upper()}:/{match.group(2)}")
    return Path(raw)


def load_yaml(path: Path) -> dict[str, Any]:
    try:
        import yaml
    except ImportError as exc:  # pragma: no cover - exercised by CLI setup
        raise RuntimeError("PyYAML is required to read the local manifest") from exc
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"manifest must be a mapping: {path}")
    return data


def nested(data: dict[str, Any], *keys: str) -> Any:
    current: Any = data
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return None
        current = current[key]
    return current


def read_sources(manifest_path: Path) -> list[dict[str, str]]:
    with manifest_path.open("r", encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    if not rows:
        raise ValueError(f"source manifest is empty: {manifest_path}")
    missing = [field for field in SOURCE_MANIFEST_FIELDS if field not in rows[0]]
    if missing:
        raise ValueError(f"source manifest missing columns: {missing}")
    if len(rows) != 622:
        raise ValueError(f"expected 622 source rows, found {len(rows)}")
    doc_ids = [row["doc_id"] for row in rows]
    if len(set(doc_ids)) != len(doc_ids):
        raise ValueError("source manifest contains duplicate doc_id values")
    if any(row["source_role"] != "source_document_jpeg" for row in rows):
        raise ValueError("source manifest contains a non-source-document row")
    return rows


def stable_seed(doc_id: str, view_id: str) -> int:
    """Derive a stable NumPy-compatible seed without Python hash randomization."""
    digest = hashlib.sha256(f"icdar_tta:grid-seed:v1:{doc_id}:{view_id}".encode()).digest()
    return int.from_bytes(digest[:4], "big") & 0x7FFFFFFF


def resize_historical(image: np.ndarray) -> np.ndarray:
    height, width = image.shape[:2]
    longest = max(height, width)
    if longest <= 1504:
        return image
    scale = 1504 / longest
    return cv2.resize(
        image,
        (max(1, int(width * scale)), max(1, int(height * scale))),
        interpolation=cv2.INTER_LINEAR,
    )


def pad_image(image: np.ndarray, params: dict[str, int]) -> np.ndarray:
    return cv2.copyMakeBorder(
        image,
        top=int(params["pad_top"]),
        bottom=int(params["pad_bottom"]),
        left=int(params["pad_left"]),
        right=int(params["pad_right"]),
        borderType=cv2.BORDER_CONSTANT,
        value=0,
    )


def encode_jpeg_rgb(image: np.ndarray) -> bytes:
    # The historical pipeline converts BGR -> RGB before effects and RGB ->
    # BGR for cv2.imwrite.  cv2.imencode is the deterministic byte equivalent
    # of cv2.imwrite for the default JPEG quality used by that pipeline.
    ok, encoded = cv2.imencode(".jpg", cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
    if not ok:
        raise RuntimeError("OpenCV JPEG encoding failed")
    return encoded.tobytes()


def load_grid_class(transform_root: Path):
    root = transform_root.resolve()
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    from chat2rec.degradations.effects.handwriting_kernel_warp import (
        HandwritingKernelWarpDegradation,
    )

    return HandwritingKernelWarpDegradation


def build_grid_warper(view_id: str, mask_root: Path, transform_root: Path, seed: int):
    grid_class = load_grid_class(transform_root)
    params: dict[str, Any] = dict(GRID_COMMON_PARAMS)
    params.update(GRID_CHANNELS[view_id])
    return grid_class(
        mask_root=mask_root,
        random_state=seed,
        visualize=False,
        warp_timeout=90.0,
        max_retries=2,
        **params,
    )


def render_view(
    source_path: Path,
    view_id: str,
    *,
    mask_root: Path,
    transform_root: Path,
    grid_warpers: dict[tuple[str, int], Any],
) -> tuple[np.ndarray, dict[str, Any], str | None]:
    source_bgr = cv2.imread(str(source_path), cv2.IMREAD_COLOR)
    if source_bgr is None:
        raise RuntimeError(f"OpenCV could not read source image: {source_path.name}")
    image = cv2.cvtColor(source_bgr, cv2.COLOR_BGR2RGB)
    image = resize_historical(image)
    seed: int | None = None
    mask_sha: str | None = None

    if view_id.startswith("P"):
        image = pad_image(image, PAD_PARAMS[view_id])
    elif view_id.startswith("G"):
        seed = stable_seed(source_path.stem, view_id)
        mask_path = mask_root / f"{source_path.stem}.tif"
        if not mask_path.exists():
            raise FileNotFoundError(f"mask missing for {source_path.stem}: {mask_path}")
        mask_sha = sha256_file(mask_path)
        key = (view_id, seed)
        warper = grid_warpers.get(key)
        if warper is None:
            warper = build_grid_warper(view_id, mask_root, transform_root, seed)
            grid_warpers[key] = warper
        image = warper.apply(image, img_path=source_path)

    return image, {"seed": seed, "mask_sha256": mask_sha}, None


def transform_spec(view_id: str, seed: int | None) -> dict[str, Any]:
    resize = {"mode": "max_dimension", "max_dimension": 1504, "interpolation": "cv2.INTER_LINEAR"}
    if view_id.startswith("U"):
        return {"family": "unchanged", "view_id": view_id, "resize": resize}
    if view_id.startswith("P"):
        return {
            "family": "pad",
            "view_id": view_id,
            "resize": resize,
            "border_mode": "constant",
            "border_value": 0,
            "pad": PAD_PARAMS[view_id],
        }
    params = dict(GRID_COMMON_PARAMS)
    params.update(GRID_CHANNELS[view_id])
    params["random_state"] = seed
    return {
        "family": "grid_warp",
        "view_id": view_id,
        "transform_id": GRID_IDS[view_id],
        "resize": resize,
        "params": params,
        "seed_schedule": "sha256(icdar_tta:grid-seed:v1:<doc_id>:<view_id>)[:4] & 0x7fffffff",
        "historical_random_state": None,
    }


def strategy_for(view_id: str) -> str:
    if view_id.startswith("U"):
        return "unchanged"
    if view_id.startswith("P"):
        return "pad"
    return "grid_warp"


def transform_id_for(view_id: str) -> str:
    if view_id.startswith("U"):
        return f"unchanged_repeat.{view_id[1:]}"
    if view_id.startswith("P"):
        return f"shift_only.variant_{int(view_id[1:]):02d}"
    return GRID_IDS[view_id]


def load_existing(path: Path) -> dict[tuple[str, str], dict[str, str]]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    return {(row["doc_id"], row["view_id"]): row for row in rows}


def write_manifest(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    ordered = sorted(rows, key=lambda row: (row["doc_id"], VIEW_ORDER.index(row["view_id"])))
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_suffix(path.suffix + ".tmp")
    with temp_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=RENDER_MANIFEST_FIELDS, extrasaction="ignore")
        writer.writeheader()
        for row in ordered:
            writer.writerow({field: row.get(field, "") for field in RENDER_MANIFEST_FIELDS})
    os.replace(temp_path, path)


def render_document(
    source_row: dict[str, str],
    *,
    views: tuple[str, ...],
    output_dir: Path,
    mask_root: Path,
    transform_root: Path,
    existing: dict[tuple[str, str], dict[str, str]],
    force: bool,
    renderer_sha: str,
    grid_renderer_sha: str,
    pad_renderer_sha: str,
) -> tuple[str, list[dict[str, Any]]]:
    """Render one document in an isolated worker.

    Grid Warp allocates substantial NumPy/OpenCV state and seeds NumPy's
    process-global RNG. Keeping the warper cache and RNG in a worker process
    prevents cross-document interleaving while preserving the exact
    per-document/view seed schedule and output bytes.
    """
    doc_id = source_row["doc_id"]
    source_path = resolve_native_path(source_row["source_path"])
    if not source_path.exists():
        raise FileNotFoundError(f"source image missing: {source_path}")
    actual_source_sha = sha256_file(source_path)
    if actual_source_sha.lower() != source_row["sha256"].lower():
        raise ValueError(f"source SHA mismatch for {doc_id}")

    rows: list[dict[str, Any]] = []
    grid_warpers: dict[tuple[str, int], Any] = {}
    for view_id in views:
        output_name = f"{doc_id}__{view_id}.jpg"
        output_path = output_dir / output_name
        prior = existing.get((doc_id, view_id))
        if (
            not force
            and prior
            and prior.get("rendered_relative_filename") == output_name
            and output_path.exists()
            and sha256_file(output_path) == prior.get("rendered_image_sha256")
        ):
            rows.append(prior)
            continue

        image, details, _ = render_view(
            source_path,
            view_id,
            mask_root=mask_root,
            transform_root=transform_root,
            grid_warpers=grid_warpers,
        )
        output_bytes = encode_jpeg_rgb(image)
        output_path.write_bytes(output_bytes)
        spec = transform_spec(view_id, details["seed"])
        rows.append(
            {
                "doc_id": doc_id,
                "view_id": view_id,
                "strategy": strategy_for(view_id),
                "transform_id": transform_id_for(view_id),
                "sample_index": VIEW_ORDER.index(view_id),
                "source_relative_filename": source_row["relative_filename"],
                "source_image_sha256": actual_source_sha,
                "mask_relative_filename": f"{doc_id}.tif" if view_id.startswith("G") else "",
                "mask_sha256": details["mask_sha256"] or "",
                "transform_spec_json": canonical_json(spec),
                "transform_spec_sha256": sha256_bytes(canonical_json(spec).encode("utf-8")),
                "seed": details["seed"] if details["seed"] is not None else "",
                "rendered_relative_filename": output_name,
                "rendered_image_sha256": sha256_bytes(output_bytes),
                "width": image.shape[1],
                "height": image.shape[0],
                "channels": image.shape[2] if image.ndim == 3 else 1,
                "codec": "JPEG",
                "codec_options": "OpenCV imencode .jpg defaults (quality=95)",
                "renderer_sha256": renderer_sha,
                "external_grid_renderer_sha256": grid_renderer_sha if view_id.startswith("G") else "",
                "external_pad_renderer_sha256": pad_renderer_sha if view_id.startswith("P") else "",
                "status": "rendered",
            }
        )
    return doc_id, rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-manifest", default="config/source_image_manifest.csv", type=Path)
    parser.add_argument("--local-manifest", default="config/data_manifest.local.yaml", type=Path)
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--transform-root", type=Path, default=None)
    parser.add_argument("--mask-root", type=Path, default=None)
    parser.add_argument("--views", default=",".join(VIEW_ORDER), help="comma-separated view IDs")
    parser.add_argument("--limit", type=int, default=None, help="render only the first N documents")
    parser.add_argument("--workers", type=int, default=1, help="bounded concurrent document workers")
    parser.add_argument("--force", action="store_true", help="regenerate existing rows")
    args = parser.parse_args()

    if args.workers <= 0:
        raise ValueError("--workers must be positive")

    local = load_yaml(args.local_manifest)
    source_root = args.source_manifest.parent
    configured_source = nested(local, "sources", "source_images", "path")
    if not configured_source:
        configured_source = nested(local, "sources", "source_images", "configured_candidate_from_run_settings")
    if not configured_source:
        raise ValueError("local manifest has no sources.source_images.path")
    source_root = resolve_native_path(configured_source)
    mask_root = args.mask_root or resolve_native_path(
        nested(local, "sources", "segmentation_masks", "roots", "resized_masks")
    )
    transform_root = args.transform_root or resolve_native_path(
        nested(local, "sources", "transform_root", "path")
    )
    output_dir = args.output_dir or resolve_native_path(
        nested(local, "sources", "scratch", "render_root") or "local_agent/runtime/modern_render"
    )
    if not source_root.exists():
        raise FileNotFoundError(f"source root does not exist: {source_root}")
    if not mask_root.exists():
        raise FileNotFoundError(f"mask root does not exist: {mask_root}")
    if not transform_root.exists():
        raise FileNotFoundError(f"transform root does not exist: {transform_root}")

    views = tuple(view.strip() for view in args.views.split(",") if view.strip())
    unknown = [view for view in views if view not in VIEW_ORDER]
    if not views or unknown:
        raise ValueError(f"views must be selected from {VIEW_ORDER}; unknown={unknown}")
    source_rows = read_sources(args.source_manifest)
    if args.limit is not None:
        if args.limit <= 0:
            raise ValueError("--limit must be positive")
        source_rows = source_rows[: args.limit]

    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = output_dir / "render_manifest.csv"
    existing = load_existing(manifest_path)
    rows: dict[tuple[str, str], dict[str, Any]] = {
        key: value for key, value in existing.items() if key[0] in {row["doc_id"] for row in source_rows}
    }
    renderer_sha = sha256_file(Path(__file__).resolve())
    grid_renderer_path = transform_root / "chat2rec" / "degradations" / "effects" / "handwriting_kernel_warp.py"
    grid_renderer_sha = sha256_file(grid_renderer_path)
    pad_renderer_path = transform_root.parent / "chat2rec_project" / "chat2rec" / "transformations" / "effects" / "pad.py"
    pad_renderer_sha = sha256_file(pad_renderer_path) if pad_renderer_path.exists() else ""
    grid_warpers: dict[tuple[str, int], Any] = {}
    started = time.time()
    processed = 0

    worker_rows = []
    for source_row in source_rows:
        worker_row = dict(source_row)
        worker_row["source_path"] = str(source_root / source_row["relative_filename"])
        worker_rows.append(worker_row)

    with ProcessPoolExecutor(max_workers=min(args.workers, len(worker_rows))) as executor:
        futures = [
            executor.submit(
                render_document,
                source_row,
                views=views,
                output_dir=output_dir,
                mask_root=mask_root,
                transform_root=transform_root,
                existing=existing,
                force=args.force,
                renderer_sha=renderer_sha,
                grid_renderer_sha=grid_renderer_sha,
                pad_renderer_sha=pad_renderer_sha,
            )
            for source_row in worker_rows
        ]
        for future in as_completed(futures):
            doc_id, rendered_rows = future.result()
            for row in rendered_rows:
                rows[(row["doc_id"], row["view_id"])] = row
            processed += 1
            if processed == 1 or processed % 5 == 0 or processed == len(source_rows):
                write_manifest(manifest_path, rows.values())
                elapsed = time.time() - started
                print(f"rendered {processed}/{len(source_rows)} documents; rows={len(rows)}; elapsed_s={elapsed:.1f}; last={doc_id}", flush=True)

    write_manifest(manifest_path, rows.values())
    expected = len(source_rows) * len(views)
    actual = len([row for row in rows.values() if row.get("status") == "rendered"])
    if actual != expected:
        raise RuntimeError(f"render manifest incomplete: expected {expected}, found {actual}")
    receipt = {
        "schema_version": 1,
        "status": "complete",
        "source_manifest": str(args.source_manifest),
        "source_count": len(source_rows),
        "views": list(views),
        "rendered_rows": actual,
        "output_dir": str(output_dir),
        "render_manifest": str(manifest_path),
        "renderer_sha256": renderer_sha,
        "external_grid_renderer_sha256": grid_renderer_sha,
        "external_pad_renderer_sha256": pad_renderer_sha,
        "historical_random_state": None,
        "modern_seed_schedule": "sha256(icdar_tta:grid-seed:v1:<doc_id>:<view_id>)[:4] & 0x7fffffff",
        "provider_calls": 0,
    }
    (output_dir / "render_receipt.json").write_text(canonical_json(receipt) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"render_modern_views: ERROR: {exc}", file=sys.stderr)
        raise
