# Validation and test plan

The repository should grow a small automated test suite as analysis code is added. The goal is to prevent silent metric drift, data leakage, path coupling, and chart/data mismatches.

## 1. Data-integrity tests

Expected checks once the historical inventory is connected:

- exactly 622 canonical source documents for the benchmark;
- unique `doc_id` values;
- expected 3,684 paper-era six-field evaluation rows after applying the recovered historical filter; separately report strict nonblank rows because the v9/v10 artifact contains one retained blank row (see [`GT_LINEAGE.md`](GT_LINEAGE.md));
- selected GT SHA-256 and lineage role agree with [`GT_LINEAGE.md`](GT_LINEAGE.md) (paper/v9/v10 `a5f0...` versus public/v7 `f1b978...`);
- exactly these six metric field names are used, while the wider 12-field GT inclusion universe is used only for the historical exclusion scan;
- no duplicate `(doc_id, field_name)` ground-truth keys;
- all evaluated predictions map to a known document and field;
- every transform ID resolves to a transform specification;
- every modern response maps to a request/model/prompt/image provenance record;
- no secret-like values or absolute local paths appear in committed portable manifests.

Reference counts should be selected by explicit GT lineage: paper/v9/v10
targets use the 3,684-row population with its one-blank-row caveat, while
public/v7 regression tables use 3,682 rows. Discrepancies must be documented
rather than hidden by changing a constant.

## 2. Normalization/CER unit tests

Create small fixture cases covering:

- case-insensitive comparison policy;
- ignored punctuation/spaces according to the paper evaluation;
- empty/nonblank field handling;
- insertion/deletion/substitution CER examples;
- Unicode normalization if present in the source labels.

## 3. Consensus/alignment unit tests

Use hand-checkable string sets to verify:

- Needleman–Wunsch scoring and gap handling;
- progressive consensus output under the canonical deterministic sample order;
- per-character vote fractions;
- word/field confidence aggregation;
- deterministic behavior across repeated runs;
- missing/failed sample behavior is explicit rather than silently treated as agreement.

Do not assert order-invariance unless the actual consensus algorithm is proven order-invariant; progressive consensus can be order-sensitive.

## 4. Paper-metric regression tests

After historical outputs are normalized, add tolerance-based regression tests for the headline values. At minimum:

- baseline field accuracy ~71.2%;
- baseline CER ~9.0%;
- best validation-consensus 10-sample field accuracy ~75.2%;
- best validation-consensus CER ~7.2%;
- Pad 10-sample field accuracy ~74.8%;
- selected historical error-correlation values.

Use exact fractions/underlying counts where recovered so tests do not depend unnecessarily on rounded paper values.

## 5. Cross-validation/leakage tests

- Augmentation selection for a fold must use only the permitted validation/training portion, never that fold's test labels.
- Modern-model first-pass transform lists must be fixed independently of the modern test results.
- Calibration and operating-threshold fitting must be cross-validated or use a separate calibration split when performance is reported on held-out fields.

## 6. Precision/coverage consistency tests

For each generated curve:

- `accepted_fields + review_fields == total_evaluated_fields`;
- `coverage == accepted_fields / total_evaluated_fields`;
- `precision == accepted_correct / accepted_fields` where accepted count > 0;
- accepted sets are nested as the confidence threshold becomes stricter for the same score definition;
- coverage is non-increasing as the threshold becomes stricter;
- sample counts and failure exclusions are explicit.

Do not require raw empirical precision itself to be perfectly monotone; finite-sample curves can fluctuate.

## 7. Cost-accounting tests

- total run cost equals the sum of included call costs;
- failed/retried calls are accounted for under a documented policy;
- currency/unit and pricing snapshot are present for estimated costs;
- per-1,000 normalization is algebraically consistent;
- mixed ensembles do not double-charge reused Pad/Grid-Warp calls when no new inference is made.

## 8. Figure reproducibility tests

Once chart scripts exist:

- each main figure has a declared source table;
- chart commands complete in a clean environment using only repository code + declared data products;
- SVG/PDF/PNG output paths are deterministic;
- figure scripts do not reach into undocumented workstation paths;
- generated annotations that contain metrics are read from the table, not duplicated as hand-entered constants.

## Suggested test command contract

When implementation begins, expose one canonical command such as:

```bash
python -m pytest
```

and one end-to-end validation command such as:

```bash
python -m icdar_tta.validate --manifest config/data_manifest.local.yaml
```

Exact package/module names can change, but the repository should converge on one documented test and one documented validation entry point.
