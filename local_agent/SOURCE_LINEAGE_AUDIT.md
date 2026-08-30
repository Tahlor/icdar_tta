# Source-lineage audit

Audit date: 2026-08-29
Scope: bounded, read-only inspection of four authorized Windows roots and named historical artifacts. No network, provider call, inference, archive extraction, raw-image copy, or external-repository edit occurred.

## Addendum — source-candidate resolution (same date, later pass)

A fifth candidate root, `configured_candidate_from_run_settings` in the ignored
local manifest (not one of the four TIFF mask roots above), was inspected with
the same bounded, read-only, no-archive-extraction method. It contains 623
direct files: 622 JPEGs plus one `622.zip` sidecar (not extracted). All 622
JPEGs have unique doc IDs, unique per-file SHA-256 hashes, and zero stem
differences against the 622-stem mask set audited above. Source-collection
SHA-256 (sorted `relative_name<TAB>byte_size<TAB>file_sha256`, UTF-8 no BOM, LF
with terminal LF): `c1c1bd78585d34da500d94cb4c838cdcd664f9d2f19615158d4e312c29afd769`.

This resolves the **622 source-document identity and SHA manifest** gate to
**PASS**. `config/source_image_manifest.csv` (622 rows: `doc_id`,
`relative_filename`, `byte_size`, `sha256`, `source_role`) and
`config/source_image_manifest.sha256` now exist and are independently
re-verifiable (row count, uniqueness, sort order, and file hash) without any
machine-specific path, image, or label text.

This addendum does **not** change any other verdict below. The canonical
3,684-field filter is still **BLOCKED** (no new inclusion/exclusion evidence
was sought or found beyond the prior pass). Exact nine-view render pixels are
still **BLOCKED** (seed/renderer/input-rule evidence is unchanged; resolving
source identity narrows but does not by itself satisfy this gate). No render
hash was fabricated.

## Verdict

The closed modern-experiment gate remains **BLOCKED**, though one prerequisite
narrowed in the addendum above. The four originally audited 622-TIFF Windows
roots are segmentation masks or derived mask renders, not source document
images; source-document identity itself is now resolved via the fifth
candidate root and is no longer a blocker on its own. The available
ground-truth and analysis artifacts produce 3,718, 3,719, 3,682, 3,678, 3,677,
3,648, or 3,732 evaluated-name candidates under evidenced predicates, never
the required 3,684. Fold assignments are recoverable, and the historical
shortlist/configuration is identifiable, but exact nine-view pixels are not
reproducible from the bounded evidence.

## Logical aliases

- `SOURCE_ROOT_WINDOWS`: parent of the four authorized Windows evidence roots.
- `PA_DEATH_ROOT`: historical PA experiment root.
- `OFFICIAL_ROOT`: official Chat2Rec PA analysis root.
- `TRANSFORM_ROOT`: historical transform-code checkout.

These aliases intentionally replace machine-specific locations.

## Windows TIFF and ZIP evidence

All counts are direct files only; no archive was extracted. TIFF collection hashes use sorted lines of `filename<TAB>byte_size<TAB>file_sha256`, UTF-8 with LF and a terminal LF.

| Logical root | Direct files | TIFFs | Other direct files | Aggregate bytes | TIFF bytes | TIFF collection SHA-256 | Determination |
|---|---:|---:|---|---:|---:|---|---|
| `SOURCE_ROOT_WINDOWS/OUTPUT_MASKS` | 623 | 622 | one 4-byte JSON containing `null` | 5,870,107,588 | 5,870,107,584 | `a5eb7d728fcf09d7f8b9b4deb45a1f56ff4ce49af9b4787f7b8005ebd5cc61ef` | mask render |
| `SOURCE_ROOT_WINDOWS/ORIGINAL_MASKS` | 623 | 622 | one 4-byte JSON containing `null` | 5,870,107,588 | 5,870,107,584 | `a5eb7d728fcf09d7f8b9b4deb45a1f56ff4ce49af9b4787f7b8005ebd5cc61ef` | byte-identical duplicate mask render |
| `SOURCE_ROOT_WINDOWS/RESIZED_MASKS` | 624 | 622 | one JPG overlay and one ZIP | 410,439,713 | 209,270,418 | `13d8a44e03eeae3f9d131521424722e8ee0193be5dd0762dd74119cb07a21428` | segmentation masks |
| `SOURCE_ROOT_WINDOWS/OUTPUT2048_MASKS` | 298 | 298 | none | 177,110,692 | 177,110,692 | not computed because this is not a complete 622 set | incomplete mask-render subset |

Set and byte comparisons:

- `OUTPUT_MASKS`, `ORIGINAL_MASKS`, and `RESIZED_MASKS` have exactly equal 622-stem sets.
- All 622 corresponding `OUTPUT_MASKS` and `ORIGINAL_MASKS` TIFFs are byte-identical.
- Zero of 622 corresponding `OUTPUT_MASKS` and `RESIZED_MASKS` TIFFs are byte-identical.
- `OUTPUT2048_MASKS` is a strict 298-stem subset of the complete set: 324 missing, zero extra. The sorted missing-stem list SHA-256 is `7b7eb11209a8355a05ff67fa6529e1b84bc7ad519e1a9cffb1f5b43316f27f5a` under `stem<LF>` serialization with a terminal LF. Its first missing stem is `41381_2421406272_0621-03214`; its last is `42342_1521003238_0765-01340`.
- `segmentation_masks.zip` is 198,238,941 bytes and contains 623 entries: 622 TIFFs plus one JPG. Uncompressed size is 212,200,772 bytes: 209,270,418 TIFF bytes plus a 2,930,354-byte JPG. Every one of the 622 TIFF streams is SHA-256-identical to its direct `RESIZED_MASKS` counterpart.

Three lexically first TIFFs were sampled per root. `OUTPUT_MASKS` and `ORIGINAL_MASKS` are uniformly 1536 by 1536, 32-bit ARGB; 82.2% to 89.9% of the 1,024 deterministic sample points were fully transparent. `RESIZED_MASKS` samples have variable dimensions (2848 by 3476, 2868 by 3500, and 3048 by 2820), are opaque 24-bit RGB, and have only 18 to 21 sampled colors. `OUTPUT2048_MASKS` has those same variable sample dimensions, is 32-bit ARGB, and has 82.0% to 88.7% fully transparent sample points. Together with the ZIP name, overlay, low-color content, exact ZIP/direct identity, and configured mask role, this establishes that all four roots contain masks/renders. None is verified as the source-document corpus.

## Ground-truth and canonical denominator

| Candidate | Rows | Columns | SHA-256 | Six edited-name result |
|---|---:|---:|---|---|
| `OFFICIAL_ROOT/raw_5164_gts_622_FIXED_v2.csv` | 622 | 62 | `ea4b7a7c39ea7179b22219bd9f8c7f16ede84fd50b3b81686b5537a1f5e4e954` | 3,718 raw and normalized nonblank fields |
| `OFFICIAL_ROOT/5164_gts.csv` | 622 | 30 | `f1b978699fda076ea75a87a991f7656de18a2195ed84b767ebb7c9758cb75727` | 3,719; three edited values differ from fixed v2 |
| `PA_DEATH_ROOT/WARP/5164_gts.csv` | 622 | 18 | `cf24e896875280560023f6c8976ca6ab32de5d0bc8426c59c00b4d58b235810d` | 3,718; all six edited fields match fixed v2 |
| `PA_DEATH_ROOT/BIG_SHIFT/CONSISTENCY/SHIFT/5164_gts.csv` | — | — | — | exact path absent |

Fixed-v2/WARP nonblank counts are: SelfGivenName 609, SelfSurname 622, FatherGivenName 622, FatherSurname 622, MotherGivenName 622, and MotherSurname 621. Repository normalization, trimmed nonblank, plausible nonmarker, and orig-plus-edited predicates all remain 3,718. Requiring all six labels on a document yields 3,648; taking every document-field pair yields 3,732.

The v7 consensus CSVs each contain 3,682 unique record/field rows: all four parent fields for 622 records and both Self fields for the same 597 records. Their `f_gt_missing` value is zero for every row. `OFFICIAL_ROOT/analysis - v7/paper/top_cer_table.csv` explicitly records `sample_count=3682` on all 20 rows. The WARP master has 68,880 rows, exactly 14 experiments by 4,920 rows. Its baseline has 3,678 six-name keys (four parent fields for 621 records and both Self fields for 597), or 3,677 after its ground-truth-missing flag.

**Canonical-filter verdict: BLOCKED.** No bounded evidence produces 3,684. The missing artifact is the historical canonical inclusion/exclusion list or generating code that explains the 34 exclusions from fixed-v2's 3,718 labels. Available historical snapshots instead encode 3,682 or 3,678. No new filter was invented.

## Fold lineage

`OFFICIAL_ROOT/analysis - v7/outputs/consensus_reliability_analysis/consensus_gw_data.csv` has SHA-256 `eaee8bb37329e5e5c32177bbe5287ce0a884148d5819e60bc2c38d44deb0d623`. It provides one consistent `f_fold` value for each of 622 record IDs. Fold record counts are 125, 125, 124, 124, and 124. Sorted `record_id<TAB>f_fold` lines with LF and a terminal LF hash to `af02ba5e2697fa71a826926ec22bc453567ec6f747e7897853a2669e69ffabbd`.

**Fold-assignment verdict: PASS for recovering assignments; BLOCKED for original generation provenance.** The snapshot is sufficient to reconstruct the assignments exactly, but no seed or generating code was found in the filename-limited search.

## Transform and render lineage

| Evidence | SHA-256 | Finding |
|---|---|---|
| `PA_DEATH_ROOT/WARP/PA_DEATH_WARP.yaml` | `bb5b5a8fe53381f3139a413d148d8aa5bd74ebde51a4854d91679007ed95164c` | active 14-experiment pipeline and five Pad dictionaries |
| `PA_DEATH_ROOT/WARP/metrics_no_punc/ensemble_selection_analysis.tsv` | `3224861466c073bb8c21e5944268a910f437a178c76a335260389dc0f19eea39` | ten ranked rows; top three v4 IDs match the frozen matrix |
| `PA_DEATH_ROOT/WARP/gemini/shift_only/run_settings.yaml` | `21b0da1a77ed2fc056e15564f8dffc108dc1ff0b19879b79e6b830652c2767e0` | exact five historical Pad dictionaries |
| `PA_DEATH_ROOT/WARP/gemini/dont_warp_text_and_lines_d003_r30_s10_std15/run_settings.yaml` | `1e200d09ce2331504824fcc11cfef662b2486790b1a09a71e5772358509f61c8` | frozen G0 configuration |
| `PA_DEATH_ROOT/WARP/gemini/warp_all_d003_r30_s10_std15/run_settings.yaml` | `1391be6765d0abaf75685945b3cea780b1290906b81030f2664f502b4fd682d0` | frozen G1 configuration |
| `PA_DEATH_ROOT/WARP/gemini/warp_hw_only_dont_warp_text_and_lines_d003_r30_s10_std15/run_settings.yaml` | `4f403fdc13c60120046b28a4b611c1b5a9db401ce4b6fd8a6a5e9f577768c239` | frozen G2 configuration |
| `TRANSFORM_ROOT/chat2rec/degradations/pipeline.py` | `74a1860489bbb42baf0a5e18ace5cea904c8c1445fc4b47c8ba740a40f36483c` | registry maps `handwriting_kernel_warp` to the located class |
| `TRANSFORM_ROOT/chat2rec/degradations/effects/handwriting_kernel_warp.py` | `089dd75ba3b203a18dd347d08885851215fe64f842e9c1c52da5cddff39bbfc8` | implementation defaults and global NumPy randomness |

Historical Grid-Warp order was resize to maximum dimension 1,504, then `handwriting_kernel_warp`, then one of five granular Pad variants. The configured warp state is null; the located implementation only seeds NumPy when a non-null state is supplied and otherwise uses global random permutations and draws. Defaults omitted from the config include target scale 1,200, automatic parameter scaling enabled, and full-image mode disabled.

**Nine-view render verdict: BLOCKED.** The source input is now hashed and linked to the mask stems, but historical rendered-image hashes, deterministic Grid seeds, and the exact Pad renderer remain absent. A `granular_shift` renderer implementation was not found in filename-limited Python/config searches across the authorized roots. Finally, frozen G0–G2 are proposed pure-warp projections, while the ranked historical runs were compound resize-plus-warp-plus-Pad pipelines. Parameters and identifiers are recoverable; exact historical pixels are not.

## Gate status

| Gate | Status | Evidence or blocker |
|---|---|---|
| 622 segmentation-mask identity and coverage | **PASS** | equal complete stem sets; complete hashes; 622 ZIP/direct matches |
| 622 source-document identity and SHA manifest | **PASS** (addendum) | fifth candidate root verified: 622 unique JPEGs, unique hashes, zero mask-stem differences; `config/source_image_manifest.csv` + `.sha256` are present in the working tree (no commit was made) |
| exact canonical 3,684 fields | **BLOCKED** | no evidenced predicate; missing canonical exclusion artifact/generator |
| recover 622 fold assignments | **PASS** | v7 snapshot and mapping hash |
| original fold-generation provenance | **BLOCKED** | seed/generator absent |
| historical transform IDs and parameter dictionaries | **PASS** | active config, ranking, and run settings hashed |
| exact nine rendered views | **BLOCKED** | Pad renderer, Grid seed/render hashes, and pure-warp lineage unresolved; source identity is now verified |
| provider/model calls | **PASS (none made)** | this audit was offline and read-only |
| modern live-experiment gate | **BLOCKED** | source, denominator, parser/render, and authorization gates remain closed |

## Commands and bounded methods

Representative redacted commands:

```text
powershell.exe -NoProfile -Command <direct-file metadata, stem-set, image-metadata, ZIP-listing script over SOURCE_ROOT_WINDOWS aliases>
powershell.exe -NoProfile -Command <streaming .NET SHA-256 over the three complete TIFF sets and ZIP TIFF streams>
PYTHONPATH=src python3 <CSV header/count/normalization and key-set aggregation script over PA_DEATH_ROOT and OFFICIAL_ROOT>
rg --glob '*.py' --glob '*.md' --glob '*.yaml' --glob '*.yml' --glob '*.txt' --glob '*.tex' <lineage terms> PA_DEATH_ROOT OFFICIAL_ROOT TRANSFORM_ROOT
```

The first hash attempt used `Get-FileHash` and failed because that cmdlet is unavailable in the installed Windows PowerShell. The failure was rerun plainly; hashing then succeeded with `System.Security.Cryptography.SHA256` streams. Searches returning no match were also rerun plainly and had exit status 1 with empty stderr.

## Artifacts and limitations

Owned changes are this report, the evidence-supported manifest updates, and the portable `config/source_image_manifest.csv` plus `config/source_image_manifest.sha256`. No render generator, provider request ledger entry, image, archive extraction, or response artifact was created.

This audit did not inspect the configured source-input location or historical transformed-output locations because they were outside the four authorized Windows roots. It did not infer image roles from directory names alone: the role conclusion uses byte identity, transparency/color statistics, ZIP membership, and historical mask configuration. Hashes establish identity, not public-release status.
