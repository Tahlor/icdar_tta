# Reproducibility and cloud contingency

## Local-first workflow

The local machine is the preferred environment for:

- discovering historical files;
- image transformation/inference;
- expensive model calls;
- inspecting individual examples;
- initial chart iteration.

This is because the local agent has access to the full historical image/output tree and can inspect failures directly.

Before reproducing any metric, read [`GT_LINEAGE.md`](GT_LINEAGE.md). The
paper/v9/v10 lineage and the public/v7 lineage use different processed GT
files and different emitted row populations (3,684 versus 3,682). The raw
3,718 `_edt` cell count is descriptive, not a metric denominator.

## Current modern-screen handoff

The current nine-view transfer screen is complete for
`gemini-3.5-flash` and `gemini-3.5-flash-lite`, with 5,598 terminal rows per
model. Its analysis deliberately uses the 3,718 raw six-name nonblank
population and does not apply the historical 3,684-row exclusion. The
predeclared 95% accepted-field precision target was not reached. The
`gemini-3.7-flash` route is blocked by HTTP 403 and the Qwen route by HTTP 500
endpoint-not-found; no full screen is claimed for either.

The raw source/render/response trees and private ledger remain outside Git.
The release-safe handoff is the redacted receipt
[`../local_agent/MODERN_FULL_RECEIPT.md`](../local_agent/MODERN_FULL_RECEIPT.md)
plus the merged CSV tables under `outputs/derived/`. The two-model screen does
not constitute a paper-lineage historical recomputation; preserve the GT
lineage labels when comparing it with the v7 or v9/v10 products.

## Cloud-ready chart contract

Chart generation should be deliberately decoupled from raw-image access.

Once derived tables exist, the current repository command is:

```bash
python3 scripts/generate_charts.py --derived-dir outputs/derived --figure-dir outputs/figures
```

A generic cloud runner should only need:

1. the repository at a known commit;
2. a Python environment defined by the repository;
3. committed or downloaded derived chart tables;
4. no model API keys for ordinary chart rendering.

Main metric charts should render to at least **SVG and PNG**; PDF is desirable for vector insertion into slides/papers.

## Proposed repository layers

- `src/` — reusable normalization, alignment, metric, cost, and plotting code.
- `scripts/` — thin orchestration/one-off migration commands when needed.
- `tests/` — unit/regression tests.
- `outputs/derived/` — compact machine-readable tables that are safe to commit.
- `outputs/figures/` — generated presentation figures; commit final selected figures if useful for deck portability.
- `runs/` — small run manifests/log summaries, not giant raw response dumps unless intentionally desired.

The current compact historical tables under `outputs/derived/` are explicitly
legacy/public v7 products. A cloud or local paper-lineage rerun must identify
the newer `a5f0...` processed GT, apply the recovered historical exclusion,
and record the v9/v10 one-blank-row convention rather than overwriting the v7
tables in place.

## Cloud options

### Option A — any Python compute environment

This is the primary contingency. Clone the repo, install the pinned environment, download/mount derived tables if they are not committed, and run the canonical chart command.

### Option B — GitHub Actions for chart regeneration

After plotting code stabilizes, add a workflow that:

- installs the pinned Python dependencies;
- runs unit/regression tests that do not require private data;
- regenerates charts from committed derived tables;
- uploads rendered figures as a workflow artifact.

Do **not** make expensive model inference a default GitHub Actions job. Inference would require explicit secret configuration and authorized access to the image corpus and should be a separate, manual workflow if ever added.

### Option C — cloud inference fallback

Only if local inference becomes unavailable:

- provide/mount an authorized copy of the source images;
- configure provider credentials through secret/environment mechanisms;
- use the same run manifest schema and exact transform definitions;
- write raw responses to durable storage and commit only manifests/derived data appropriate for the repository.

## Environment requirements

Once analysis code is present, pin versions via `pyproject.toml`/lockfile or an equivalent reproducible environment. Prefer a small common stack (Python, pandas/polars, numpy/scipy, matplotlib, pyarrow as needed) rather than notebook-only dependencies.

Notebooks may be used for exploration but should not be the only way to regenerate a final figure.

## Determinism/provenance

Every generated chart should be traceable to:

- repository commit SHA;
- source-table checksum;
- chart script/version;
- model/run IDs represented;
- metric/filtering definition;
- generation timestamp if useful.

The figure itself does not need to display all provenance; a sidecar manifest or build log can carry it.
