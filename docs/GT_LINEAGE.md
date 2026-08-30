# PA Death 622 ground-truth and evaluation lineage

Status: **field selector and historical exclusion rule recovered; one blank-row
artifact remains explicit** (2026-08-30, America/Denver).

This is the current ground-truth contract for the 622-record replication. It
supersedes the earlier “34 exclusions are unresolved” interpretation in the
bounded audit receipts. Those receipts remain in `local_agent/` as an audit
trail; they must not be used as the current evaluation specification.

## Executive decision

The historical metric selector is the following six fields, in the order used
by the collapse script:

```text
SelfGivenName
SelfSurname
FatherGivenName
FatherSurname
MotherGivenName
MotherSurname
```

This is evidenced independently by:

- `chat2rec/processing/3_7_COLLAPSE.py`, `TARGET_FIELDS`;
- `chat2rec/processing/analysis/configs/pa_death_records622_analysis_official_v2.yaml`,
  `filters.field_names`; and
- the field names in the paper-era v9/v10 consensus tables.

The historical record exclusion is also recoverable from
`chat2rec/processing/common.py`, `_add_flags`:

1. Build the ground-truth long table from the wider configured inclusion
   universe (the six name fields plus birthplaces and combined names).
2. Use the original ground-truth value first, with the edited value as the
   fallback when the original is blank.
3. Find records where any included ground-truth value contains one of the
   case-insensitive regex terms `stillborn`, `infant`, `know`, `maiden`, or
   `baby`.
4. Set `f_exclude` only for rows whose `field_name` starts with `Self`, then
   drop those rows.

On the newer processed GT used by the v9/v10 artifacts, this flags 24 records.
The six-field rectangular population is therefore:

```text
622 records × 6 fields − 24 records × 2 Self fields = 3,684 rows
```

This is historical behavior, not a newly proposed semantic exclusion rule.
The `know` term is an unanchored substring regex and can match text such as
“unknown”; reproduce it only when reproducing the paper-era pipeline.

## The 3,684 blankness caveat

The paper describes 3,684 fields as nonblank, but the machine-readable v9 and
v10 consensus tables expose 3,684 six-field rows with this distribution:

| Field | Rows |
|---|---:|
| `FatherGivenName` | 622 |
| `FatherSurname` | 622 |
| `MotherGivenName` | 622 |
| `MotherSurname` | 622 |
| `SelfGivenName` | 598 |
| `SelfSurname` | 598 |
| **Total** | **3,684** |

Those tables contain 3,683 rows with `f_gt_missing=0` and one retained blank
`MotherSurname` row with `f_gt_missing=1`. The analysis configuration requests
`f_gt_missing: 0`, but that condition is not reflected in the emitted v9/v10
row count. Consequently:

- call 3,684 the **paper-era six-field evaluation population/row count**;
- do not describe every one of those rows as nonblank without checking the
  particular artifact;
- if a strict nonblank-only metric is required, report the artifact’s 3,683
  nonblank rows separately; and
- do not silently delete the blank row or silently change the historical
  denominator during replication.

The raw edited-name count of 3,718 is a different statistic. It counts nonblank
`_edt` cells in the six name columns before applying the historical record-level
exclusion and is not evidence of a missing 34-row filter.

## Exact source lineages

Hashes are SHA-256 over the exact external files. Paths are logical paths from
the local inventory, not portable machine paths.

| Lineage | Artifact | Rows / columns | SHA-256 | Use |
|---|---|---:|---|---|
| Raw fixed-v2 | `chat2rec_analysis/projects/pa_death_records622_official/raw_5164_gts_622_FIXED_v2.csv` | 622 / 62 | `ea4b7a7c39ea7179b22219bd9f8c7f16ede84fd50b3b81686b5537a1f5e4e954` | Raw label/traceability source. Six `_edt` name cells: 3,718 nonblank. |
| Paper/v9/v10 processed | `chat2rec_analysis/projects2/pa_death_records622_official/5164_gts.csv` | 622 / 30 | `a5f0f9e45d78f270d213f31a1f765bd7a5cdd587f0020cdeb1d0b664184aa306` | Processed GT whose relevant name/place values match fixed-v2; use for paper-era v9/v10 lineage. |
| Paper v9 Grid-Warp | `.../analysis - v9/outputs/consensus_reliability_analysis/consensus_gw_data.csv` | 3,684 rows | `d988c53c11eb7805f5bfeae8568200c074f2caeccbed5cede9599726e7a4ded1` | Machine-readable paper-era consensus evidence. |
| Paper v9 Lite | `.../analysis - v9/outputs/consensus_reliability_analysis/consensus_gwLITE_data.csv` | 3,684 rows | `a6badb159b945a50ad2488c2fbe9aabf593c5d453cea97cf136d5d99e1150f72` | Same six-field row population. |
| Paper v10 Lite | `.../analysis - v10/outputs/consensus_reliability_analysis/consensus_gwLITE_data.csv` | 3,684 rows | `b84fc6c93535db030c1cc1e048245999444ccbb25b5b9b24d6efb64006e13d7e` | Independent later snapshot with the same six-field population. |
| Legacy/public processed | `chat2rec_analysis/projects/pa_death_records622_official/5164_gts.csv` | 622 / 30 | `f1b978699fda076ea75a87a991f7656de18a2195ed84b767ebb7c9758cb75727` | Older processed GT used by the v7 reliability outputs and packaged as the public release official CSV. Six `_edt` name cells: 3,719 nonblank. |

The older WARP and SHIFT copies are separate schema groups, not interchangeable
aliases:

- WARP: 18 columns, SHA-256
  `cf24e896875280560023f6c8976ca6ab32de5d0bc8426c59c00b4d58b235810d`;
- SHIFT and related roots: 20 columns, SHA-256
  `14219f17eeaaf45ffa4cec49f624de1edb3a739b40a87f0f838355a7fa414ccd`.

Their six relevant name values agree with fixed-v2, but their processed/public
lineage and emitted metric populations must still be identified by artifact.

## Why 3,682 appears in this repository

The v7 consensus reliability tables use the older `f1b978...` processed GT
lineage. They contain 3,682 rows: four parent fields for all 622 records and
two Self fields for 597 records. That is consistent with the older lineage’s
25 historical Self-record exclusions:

```text
622 records × 6 fields − 25 records × 2 Self fields = 3,682 rows
```

The public GitHub release packaging commit `35a3bd4` records the same
`f1b978...` file at `data/official/5164_gts.csv`, while also including the raw
fixed-v2 traceability file. The public release and v7 snapshot therefore do
not provide the same processed GT lineage as the paper-era v9/v10 3,684-row
tables. This is the answer to “which GT does the GitHub repo use?”: the public
official archive uses the older `f1b978...` lineage.

Existing `icdar_tta` derived tables based on v7 remain valid as **legacy/public
3,682-row products**, but are not paper-v9/v10 3,684-row re-computations. Keep
their denominator labels and receipts explicit until a separate six-field
paper-lineage recomputation is made.

## What agents should use

For a paper-era reproduction, use the newer processed GT hash
`a5f0f9e4...`, the six fields above, and the historical `_add_flags` behavior;
then record how the one blank v9/v10 row is handled. For a public-release or
v7 reproduction, use the older `f1b978...` hash and label results as the
3,682-row legacy lineage.

The cloud agent should receive this contract, the portable manifest, the
historical script/config references, and compact derived tables. It does not
need the private raw label CSV, raw model-response trees, or full image corpus
in Git. Machine-specific paths stay in the ignored local manifest; no label
values or credentials belong in the portable handoff.
