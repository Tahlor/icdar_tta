# Data and path contract

The local machine is expected to contain historical images and outputs that should not necessarily be copied into this repository. This document defines how local and cloud agents refer to them reproducibly.

## Two-manifest pattern

### `config/data_manifest.local.yaml`

- Machine-specific.
- May contain absolute local paths.
- **Ignored by Git and never committed.**
- Used by local scripts to resolve actual data locations.

### `config/data_manifest.yaml`

- Portable/redacted provenance manifest.
- May be committed once the inventory is known.
- Must not contain credentials or sensitive absolute paths.
- Records logical dataset IDs, counts, hashes, public URLs when appropriate, relative layouts, and notes on where an authorized agent can obtain/mount the data.

Use `config/data_manifest.example.yaml` as the schema starting point.

## Logical data roots

Scripts should resolve data through logical keys rather than embedding workstation paths:

- `source_images`
- `ground_truth`
- `fold_assignments`
- `historical_responses`
- `historical_augmentations`
- `shift_analysis`
- `paper_code`
- `usage_logs`
- `modern_responses`
- `scratch`

If the local inventory reveals additional important sources, add keys rather than hard-coding paths in analysis scripts.

## Required inventory record

For every logical source, record when applicable:

- description;
- filesystem path in the local manifest;
- file count / row count;
- byte size;
- format;
- dataset or run date;
- SHA-256 for key manifests/files, or a generated file-index checksum for large trees;
- whether the source is immutable/raw or derived;
- whether it is public/releasable;
- upstream source or URL if public;
- associated model/prompt/config version;
- known caveats.

## Canonical IDs

### Documents

Create or recover a stable `doc_id` mapping. Never use an absolute path as the document identifier.

### Fields

Use stable field names matching the evaluation schema. The paper evaluation focused on nonblank given-name/surname fields for the decedent, mother, and father; the inventory should recover the exact canonical names used by the historical scripts.

A field observation should be uniquely addressable by at least:

`(doc_id, field_name, model_id, run_id, strategy, transform_id, sample_index)`

### Transforms

Every transformed image/output must have a `transform_id` tied to a structured transform specification, e.g. family + parameters + seed/direction/offset. Do not use a filename alone as the transform definition.

## Raw model-response provenance

Each new response should capture:

- provider;
- exact model ID/version returned/used;
- request timestamp and timezone/UTC;
- prompt/schema hash;
- source image hash;
- transform ID;
- exposed generation parameters;
- response text/JSON before normalization;
- parser version;
- status/retry count/error;
- usage/tokens/units when returned;
- latency;
- pricing snapshot ID or billing source when cost is derived.

## Derived-data contract

The repository may commit compact, non-sensitive derived tables needed to reproduce presentation charts. Preferred derived outputs:

- normalized field predictions;
- strategy summary metrics;
- error-correlation summary;
- precision/coverage curves;
- shift-agreement series;
- per-run usage/cost;
- review frontier;
- cross-model operating points.

If field-level predictions themselves cannot be public, commit aggregate chart tables and provide a script that reads the authorized field-level location.

## Cloud fallback

Cloud chart generation should **not require raw images** for ordinary metric charts. The local pipeline should commit or publish the necessary derived chart tables so a generic cloud environment can regenerate SVG/PDF/PNG.

Inference in the cloud is a separate concern: it requires an authorized image source/mount plus provider credentials. Do not design chart reproducibility to depend on inference being available in the same environment.
