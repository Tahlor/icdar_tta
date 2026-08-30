# Expanded Canonical 3,684-Pair Filter Recovery Audit

Status: **NEGATIVE — acceptance evidence not found.** No canonical filter or
sidecar was created.

## Decision

The acceptance rule required both:

1. a named artifact or generator visibly defining the included/excluded
   population; and
2. an independent count of exactly **3,684 `doc_id`/`field_name` pairs**.

Neither condition was established in the fixed search scope. The only literal
`3684` body hit in a non-label table is an incidental numeric signal value in a
10-row peak-analysis table, not a population count. Therefore it is unsafe to
invent a predicate, copy private labels, or create
`config/canonical_field_filter.csv` or a checksum sidecar.

## Live state verified before the audit

- Workspace: the `icdar_tta` checkout designated in `local_agent/TASK.md`.
- Branch: `master`.
- HEAD: `cebf7778cea92692da9837f8914ae0b61a29c399`.
- The workspace already contained substantial tracked and untracked changes;
  none was cleaned, reset, checked out, staged, committed, or overwritten.
- `ANALYSIS_ROOT`: configured official
  `chat2rec_analysis/projects/pa_death_records622_official` project.
- `HIST_ROOT`: the Windows `PA_DEATH` project designated by `TASK.md`; all
  inspection was performed through `powershell.exe` using exact `D:` paths.
- `RELEASE_ROOT`: official `pa-death-records-622` checkout designated by
  `TASK.md`; its `main` worktree was clean. The containing
  `chat2rec_analysis` worktree was dirty and remained untouched.
- No pre-existing expanded audit, canonical filter CSV, or filter checksum
  sidecar was present.

## Exact fixed scope

### Official analysis root

Directory names were inspected directly. The directly present versions were:

- `analysis - v1`
- `analysis - v2 - seam carving`
- `analysis - v3`
- `analysis - v4`
- `analysis - v5`
- `analysis - v6`
- `analysis - v6a`
- `analysis - v7`

For each version, only direct files and direct files in
`best_consensus_CER`, `best_consensus_oracle`, and
`outputs/consensus_reliability_analysis` (when present) were enumerated. This
was exactly 28 directories: the eight version roots; 16 `best_consensus_*`
directories; and the four reliability directories under v5, v6, v6a, and v7.
No `projects2` directory was directly present, so no `projects2/v8`, `v9`, or
`v10` directory existed to inspect.

Content eligibility was limited to files under 2 MiB with an allowed
code/config/report/notebook/TeX/Markdown type and a filename containing one of:
`canonical`, `filter`, `exclude`, `exclusion`, `evaluable`, `valid`, `field`,
`ground`, `truth`, `3684`, or `3718`.

Result: **237** direct files enumerated; **0** files over 2 MiB; **0** files met
the complete filename/type/size content rule. Consequently no file content was
read outside the rule and there were no official-analysis content candidates
to hash.

### Historical `PA_DEATH` root

Only direct files and files directly inside one level of subdirectories were
considered in the five named roots. Images were filename-enumerated only; no
image bytes were read. `gemini`, raw, response, prediction, database, image,
and archive trees were excluded. Files at least 2 MiB were not read. Eligible
content types were code, config, report, notebook, TeX, Markdown, CSV, and TSV.

| Relative root | Files enumerated | Eligible under 2 MiB | Excluded at least 2 MiB | Candidates |
|---|---:|---:|---:|---:|
| `BIG_SHIFT` | 18 | 8 | 7 | 5 |
| `CVPR_ANALYSIS` | 46 | 21 | 1 | 1 |
| `CONSISTENCY` | 17 | 7 | 8 | 4 |
| `SHIFT` | 30 | 12 | 16 | 6 |
| `WARP` | 31 | 13 | 15 | 4 |
| **Total** | **142** | **61** | **47** | **20** |

A table was treated as label-bearing when its filename or header identified
labels, edited/original ground truth, `gt_value`, prediction values, or
record/field rows. Such tables were inspected only for header, data-row count,
and SHA-256. No row values are retained in this report.

#### Candidate inventory

Repeated hashes below are intentional and independently show byte-identical
files in different shortlist locations.

| Candidate relative to `HIST_ROOT` | Data rows | SHA-256 | Interpretation |
|---|---:|---|---|
| `BIG_SHIFT/5164_gts.csv` | 622 | `14219f17eeaaf45ffa4cec49f624de1edb3a739b40a87f0f838355a7fa414ccd` | Document-level label table; no `doc_id`/`field_name` pair list. |
| `BIG_SHIFT/5164_gts_no_post_processing.csv` | 622 | `14219f17eeaaf45ffa4cec49f624de1edb3a739b40a87f0f838355a7fa414ccd` | Byte-identical document-level label table. |
| `BIG_SHIFT/metrics_no_punc/experiment_level_consensus.csv` | 9,842 | `12ae3880b56d279cab398910eda0826d7cd87c216a2dbeaa6415100a77a635ef` | Label-bearing experiment/record/field rows; not a named canonical filter. |
| `BIG_SHIFT/metrics_no_punc/name_fields_category_summary.csv` | 1 | `add6f6f064374bbe7091db2153caaf1c57581118e24f040958297585f311ca10` | Aggregate summary, not a pair list. |
| `BIG_SHIFT/metrics_no_punc/name_fields_consensus_by_category.csv` | 3,674 | `ff2c5845e7d900e61edc4169e2a723ddaa2c182b1b97e08f27c8ee0c283ac7e1` | Record/field result rows; count is not 3,684. |
| `CVPR_ANALYSIS/combined_vertical_peaks.csv` | 10 | `30d8ff6251d80cf8b9fb859901405b8b29291f6f8de432f4659bfbef1687dfef` | Literal `3684` occurs on line 4 as part of a numeric peak/signal value; not a pair count. |
| `CONSISTENCY/5164_gts.csv` | 622 | `14219f17eeaaf45ffa4cec49f624de1edb3a739b40a87f0f838355a7fa414ccd` | Document-level label table. |
| `CONSISTENCY/5164_gts_no_post_processing.csv` | 622 | `14219f17eeaaf45ffa4cec49f624de1edb3a739b40a87f0f838355a7fa414ccd` | Byte-identical document-level label table. |
| `CONSISTENCY/metrics_no_punc/name_fields_category_summary.csv` | 1 | `fd469eb5e9e15f83e6e61f1c9f33311768413af3cd559b1ca521c68b37ce37e7` | Aggregate summary. |
| `CONSISTENCY/metrics_no_punc/name_fields_consensus_by_category.csv` | 3,678 | `76f1d1de2af20c1447c370c065717ea3d1784a0f0bb7fa909be85d6352d61f30` | Record/field result rows; count is not 3,684. |
| `SHIFT/5164_gts.csv` | 622 | `14219f17eeaaf45ffa4cec49f624de1edb3a739b40a87f0f838355a7fa414ccd` | Document-level label table. |
| `SHIFT/5164_gts_no_post_processing.csv` | 622 | `14219f17eeaaf45ffa4cec49f624de1edb3a739b40a87f0f838355a7fa414ccd` | Byte-identical document-level label table. |
| `SHIFT/metrics_no_punc/name_fields_category_summary.csv` | 1 | `55aa736605b4d32072c62491b1adca1cd3d3bcc33452b430279a2d0aca7670a0` | Aggregate summary. |
| `SHIFT/metrics_no_punc/name_fields_consensus_by_category.csv` | 3,677 | `78b4ac5a720a915a2d8ebd48725c1457ab7fe24b8f7ccb21e84244db02336582` | Record/field result rows; count is not 3,684. |
| `SHIFT/metrics_no_punc_v1/name_fields_category_summary.csv` | 1 | `41176d1533f28ccf73c41cdbeed733df6446ddf70792064bf8bdff928dba0396` | Aggregate summary. |
| `SHIFT/metrics_no_punc_v1/name_fields_consensus_by_category.csv` | 3,678 | `c79cfa7e0e0ac7917a1a81e487dc44bb1c01b963226dac9fe8922f47e1f87041` | Record/field result rows; count is not 3,684. |
| `WARP/5164_gts.csv` | 622 | `cf24e896875280560023f6c8976ca6ab32de5d0bc8426c59c00b4d58b235810d` | Document-level label table with a different header shape. |
| `WARP/5164_gts_no_post_processing.csv` | 622 | `cf24e896875280560023f6c8976ca6ab32de5d0bc8426c59c00b4d58b235810d` | Byte-identical document-level label table. |
| `WARP/metrics_no_punc/name_fields_category_summary.csv` | 3 | `c648fb7645cca7fe6d58e2469a3dbc71d2858f88eef0e6384b531da09805c1d7` | Aggregate summary. |
| `WARP/metrics_no_punc/name_fields_consensus_by_category.csv` | 11,034 | `b2f9ccc66fb2e9666ac125a49c6f289ac5404e807266abd887c499b121724412` | Multi-category record/field result rows; not a canonical pair list. |

There are 20 candidate path occurrences and 14 distinct hashes. The observed
data-row counts are 622, 9,842, 1, 3,674, 10, 3,678, 3,677, 3, and 11,034;
none equals 3,684.

### Official release checkout

Only code/config/docs were inspected: `DATA_DICTIONARY.md`, `LICENSE.md`,
`README.md`, `RELEASE_NOTES.md`, and `scripts/verify_release.py`. All five were
under 2 MiB. Exactly one contained a requested token:

| Candidate | Size | SHA-256 | Match |
|---|---:|---|---|
| `README.md` | 4,341 bytes | `8c4273c2fc0158fc66f5d9443c1c8454f12def084f4309e54352b9eb16cfc6cb` | Line 82 calls the release archive the canonical public download. |

That statement establishes release provenance only. It does not define an
included/excluded field population, identify `doc_id`/`field_name` pairs, or
provide a generator/count for 3,684 pairs.

## Exact-token result

The case-insensitive literal search set was: `3684`, `3,684`, `3718`, `3,718`,
`canonical`, `evaluable`, `exclusion`, `exclude`, `field_filter`, `inclusion`,
`f_gt_missing`, `doc_id`, and `field_name`.

- Official analysis: no file passed the mandatory filename/type/size content
  gate, so there was no permitted content candidate.
- Historical root: label-bearing tables exposed `field_name` in headers but
  use `record_id`, not `doc_id`; no header or allowed code/config/report text
  defined a canonical inclusion/exclusion population. The only non-label body
  hit relevant to the target number was the incidental `3684` signal value in
  `combined_vertical_peaks.csv` described above.
- Release checkout: only the release-archive meaning of `canonical` appeared.
- No named artifact or generator connected `3718`/`3,718` to an evidenced
  34-pair exclusion, and no permitted evidence independently counted 3,684
  `doc_id`/`field_name` pairs.

## Excluded scope and safety boundaries

This was deliberately not an exhaustive disk search. The following remained
out of scope:

- any directory outside the fixed roots and relative directories listed above;
- recursion below the allowed direct/one-subdirectory depth;
- nonexistent `projects2/v8-v10` directories;
- raw response, prediction, image, database, Gemini, and archive trees;
- image bytes, private label row values, raw model response bodies, archives,
  databases, and files at least 2 MiB;
- files outside allowed code/config/report/notebook/TeX/Markdown/tabular types;
- network/provider access, model calls, inference, credentials, and live route
  tests.

An intermediate PowerShell attempt failed at parse time and was rerun plainly,
showing the same parser error. A corrected attempt then found that this Windows
PowerShell environment did not provide `Get-FileHash`; its blank hashes were
not used. The final bounded rerun used .NET SHA-256 and completed with exit 0
and no stderr. A stricter header-based table classification was used for the
final inventory so label-bearing tables retained only headers, counts, and
hashes in this artifact.

## Disposition

- **No filter accepted or created.**
- `config/canonical_field_filter.csv`: not created.
- Any canonical-filter checksum/sidecar: not created.
- Existing manifests, frozen budget/model/transform values, historical tables,
  and request ledger: not modified.
- Live provider gate: remains closed.
- No file outside `local_agent/CANONICAL_FILTER_EXPANDED_AUDIT.md` was created
  or modified by this audit.

## Validation

All checks were offline and run from the repository root.

1. `PYTHONPYCACHEPREFIX=/tmp/icdar_tta_compileall python3 -m compileall -q src scripts tests`
   exited 0 with empty stdout and stderr.
2. `PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -q`
   exited 0 with exact result:

   ```text
   ----------------------------------------------------------------------
   Ran 207 tests in 2.231s

   OK
   ```
3. `PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 python3 -m icdar_tta.validate --portable-manifest config/data_manifest.yaml --manifest config/data_manifest.local.yaml`
   exited 0. It reported PASS for normalize, parser, consensus, portable-manifest
   secrets/shape, and local-manifest shape; the absent optional field-table gate
   was explicitly skipped; final line was `Overall: PASS (0 hard failure(s))`.
4. Independent `yaml.safe_load` parsing exited 0:
   - `config/data_manifest.yaml`: mapping, schema version 1, 17 source keys.
   - `config/data_manifest.local.yaml`: mapping, schema version 1, 12 source keys.
5. The owned-report redaction scan found zero WSL absolute paths, Windows
   absolute paths, UNC paths, secret assignments, private-key headers, private
   usernames, and trailing-whitespace lines; `REDACTION_SCAN PASS`.
6. Standard and independent Python SHA-256 computations agreed. The final-byte
   checksum is reported after the final artifact-sensitive recheck.
7. `git diff --check` exited 0 with no diagnostics.
8. Existence/disposition check confirmed this report and its terminal marker,
   and confirmed that neither canonical-filter CSV nor checksum sidecar exists.

CANONICAL_FILTER_EXPANDED_AUDIT_DONE
