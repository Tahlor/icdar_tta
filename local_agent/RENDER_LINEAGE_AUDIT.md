# Render-lineage recovery audit

**Status: BLOCKED**
**Audit date:** 2026-08-29
**Repository HEAD inspected:** `cebf7778cea92692da9837f8914ae0b61a29c399`
**Owned artifact:** `local_agent/RENDER_LINEAGE_AUDIT.md`

## Executive determination

The verified 622-document source manifest is sufficient to identify every source JPEG, but it is **not** a render manifest. The exact historical nine-view pixels cannot be recovered or regenerated from the bounded evidence.

The historical Grid Warp class, its segmentation-mask lookup rule, the three frozen parameter dictionaries, and their source hashes are recoverable. The historical `granular_shift` Pad renderer is not: the active historical configuration names that effect, but the inspected registry does not register it, and the available `shift.py` implements translation parameters rather than `pad_left`, `pad_right`, `pad_top`, and `pad_bottom`. Grid Warp used global NumPy randomness with `random_state: null`; no deterministic per-document/per-view seeds or rendered-image hashes were found. The exact configured historical transform-output root is absent.

Accordingly, this audit does **not** create a render manifest, does **not** invent seeds or Pad semantics, does **not** claim that U0–G2 render reproducibly, and does **not** open the provider-call gate.

## Bounded scope and logical aliases

The inspection was read-only except for this report. It covered only:

- repository contracts, the frozen matrix, existing source-lineage evidence, both data manifests, `config/source_image_manifest.csv`, and existing `src/`, `scripts/`, and tests;
- `PA_RELEASE_ROOT`: the known official PA release checkout;
- `PA_DEATH_ROOT`: the known historical PA experiment root, limited to named WARP configuration and direct run metadata;
- `TRANSFORM_ROOT`: the authorized `chat2rec/degradations` checkout;
- `SOURCE_IMAGE_ROOT`, `MASK_ROOT`, and `HISTORICAL_RENDER_ROOT`: paths already named by the ignored local manifest or historical WARP configuration, inspected only with bounded direct-file metadata/hash operations.

No unrelated home, provider-cache, raw-response, archive, or image tree was recursively scanned. No archive was extracted; no image was opened, copied, committed, or printed. No provider, network, cloud, or inference call was made. The pre-existing dirty worktree was preserved; no clean, reset, checkout, staging, or commit occurred.

## Logical evidence table

Hashes are SHA-256 over exact file bytes unless a row explicitly describes a collection serialization.

| Logical evidence | SHA-256 | Direct finding |
|---|---|---|
| `config/source_image_manifest.csv` | `7ad5e7a065bf8bd262953d8faf8e34344e861333c4655eff72bf80aee90f25ee` | 622 data rows; source JPEG identities and hashes only |
| Source collection serialization | `c1c1bd78585d34da500d94cb4c838cdcd664f9d2f19615158d4e312c29afd769` | Sorted `relative_name<TAB>byte_size<TAB>file_sha256`, UTF-8, LF, terminal LF |
| `config/source_image_manifest.sha256` | `78f07f1bbe03cb70677bfec18d6a7d0bca0acf80725d91f2a6a04932547fcd7b` | Sidecar contains the exact CSV hash and row/serialization notes |
| `config/data_manifest.yaml` | `42c3ad634ab25ec017ded2aedb97f5e9b91586b73af7b01ac77d8fb6171c3a26` | Correctly distinguishes source hashes from unresolved render lineage |
| `local_agent/EXPERIMENT_MATRIX.md` | `a2729cbc56cdc206ea1aa4c275d54dee6d8fd701e1a186db0a6e910f625cea8d` | Frozen U0–G2 IDs; requires a rendered-image SHA-256 per view |
| `local_agent/SOURCE_LINEAGE_AUDIT.md` | `130134bfc223cd13e1a9871925e03bd2964951c4e30bc212618aab688a1eae26` | Prior prose checked against sources; not treated as render evidence itself |
| `local_agent/ROUTE_AUDIT.md` | `74bb608eb27deb59649a5bb4ee5bd414a1f16685fa0e6898e8af5c7584dd6d9b` | Route transport descriptions, not an executable frozen transport in this repository |
| `PA_RELEASE_ROOT/README.md` | `8c4273c2fc0158fc66f5d9443c1c8454f12def084f4309e54352b9eb16cfc6cb` | Public landing page identifies originals; it contains no render lineage |
| `PA_RELEASE_ROOT/scripts/verify_release.py` | `6123bc2091c428ef7b71b5972cdfcca51fd84d48f71ee70cb48380fc1b8e5ba5` | Verifies 622 archive images/labels; it does not render U/P/G views |
| `PA_DEATH_ROOT/WARP/PA_DEATH_WARP.yaml` | `bb5b5a8fe53381f3139a413d148d8aa5bd74ebde51a4854d91679007ed95164c` | Active resize → Grid Warp where applicable → five granular Pad variants |
| `PA_DEATH_ROOT/WARP/metrics_no_punc/ensemble_selection_analysis.tsv` | `3224861466c073bb8c21e5944268a910f437a178c76a335260389dc0f19eea39` | Ten ranking rows; supports frozen IDs, not historical pixels |
| `PA_DEATH_ROOT/WARP/gemini/shift_only/run_settings.yaml` | `21b0da1a77ed2fc056e15564f8dffc108dc1ff0b19879b79e6b830652c2767e0` | Exact five Pad dictionaries; no Pad implementation or image hashes |
| G0 run settings | `1e200d09ce2331504824fcc11cfef662b2486790b1a09a71e5772358509f61c8` | `dont_warp_text_and_lines_d003_r30_s10_std15` |
| G1 run settings | `1391be6765d0abaf75685945b3cea780b1290906b81030f2664f502b4fd682d0` | `warp_all_d003_r30_s10_std15` |
| G2 run settings | `4f403fdc13c60120046b28a4b611c1b5a9db401ce4b6fd8a6a5e9f577768c239` | `warp_hw_only_dont_warp_text_and_lines_d003_r30_s10_std15` |
| `TRANSFORM_ROOT/pipeline.py` | `74a1860489bbb42baf0a5e18ace5cea904c8c1445fc4b47c8ba740a40f36483c` | Registers Grid Warp, `shift`, and `deterministic_shift`; no `granular_shift` |
| `TRANSFORM_ROOT/effects/shift.py` | `ffd94284ff4c302c51852b03b425c7794079a138882e17a4ac10353b092781d5` | Translation/warp implementation; no four-side Pad parameters |
| `TRANSFORM_ROOT/effects/resize.py` | `08711d82b7315e5f0fcdcaa58184d68aed6e237f125867f8bdef361aa394339e` | Random percentage resize; does not implement historical `resize_mode: max_dimension` adapter semantics |
| `TRANSFORM_ROOT/effects/handwriting_kernel_warp.py` | `089dd75ba3b203a18dd347d08885851215fe64f842e9c1c52da5cddff39bbfc8` | Active Grid Warp class and global NumPy randomness behavior |
| `TRANSFORM_ROOT/effects/seam_removal.py` | `bce05f38fcf3f9bcddf31a267359d1ac99e98ce0891a1877a87c8e14cc155aea` | Imported mask mixin: `mask_root / (source_stem + mask_suffix)` and mask normalization |
| `TRANSFORM_ROOT/generate_variants.py` | `b545c0e860dae1a0ea13c36e12f2b0cad84aee1881da2f22b3a9b2eea85af39f` | Generic helper expects `degradation_config`; it is not a command for the historical `transformation_config` schema |
| `HISTORICAL_RENDER_ROOT` | unavailable | Exact configured root does not exist; therefore no surviving G0–G2 files or sidecars were hashable there |

## 1. Historical granular Pad/shift renderer

**Determination: not recoverable from the scoped evidence.**

The named historical configuration and `shift_only` run settings recover these exact first-three dictionaries:

| View | Historical ID | Frozen dictionary |
|---|---|---|
| P0 | `shift_only.variant_00` | `{"pad_left":16,"pad_right":16,"pad_top":16,"pad_bottom":16}` |
| P1 | `shift_only.variant_01` | `{"pad_left":8,"pad_right":24,"pad_top":8,"pad_bottom":24}` |
| P2 | `shift_only.variant_02` | `{"pad_left":28,"pad_right":4,"pad_top":28,"pad_bottom":4}` |

The configuration also establishes source order and that the historical WARP pipeline first requested maximum-dimension resize to 1,504, then Grid Warp where present, then `granular_shift`. It does **not** establish the missing pixel operation: canvas color/value, channel handling, whether dimensions expand or content translates/crops, library interpolation/encoding behavior, or the manager adapter that maps `transformation_config` into executable degraders.

The directly inspected registry contains 13 keys—`albumentations`, `blur`, `composite`, `deterministic_shift`, `gaussian_noise`, `gridwarp`, `gridwarp2`, `handwriting_aware_gridwarp`, `handwriting_kernel_warp`, `identity`, `resize`, `seamcarve`, and `shift`—and `granular_shift` is absent. Attempting to resolve that type would reach `ValueError("Unsupported degradation type: granular_shift")` once runtime dependencies are available. The available `shift.py` cannot consume the Pad dictionaries without inventing a mapping. The available `resize.py` likewise does not implement the historical `max_dimension` parameter pair, indicating that an unlocated manager-side adapter supplied additional semantics.

Therefore P0/P1/P2 cannot be rendered as frozen historical views from a named implementation. Implementing ordinary image padding now would be a new renderer, not recovery of the historical renderer.

## 2. Historical Grid Warp implementation

**Determination: implementation and dictionaries recoverable; historical pixels and deterministic schedule not recoverable.**

`pipeline.py` maps `handwriting_kernel_warp` to `HandwritingKernelWarpDegradation`. Dependency-free AST inspection confirmed that its constructor accepts every frozen G parameter, including the channel lists and omitted defaults. The mask mixin derives a mask from the source image stem plus `.tif` under the configured mask root. The implementation requires `img_path`; absent an image path or mask, it returns the original image with an unapplied reason.

Shared frozen values are `prob=1.0`, `point_density=0.003`, `base_radius=30.0`, `boundary_safety=1.0`, `min_radius=5.0`, `warp_strength=10.0`, `noise_std=1.5`, `falloff_type="gaussian"`, `region_based=true`, `region_margin=20`, `min_influence=0.01`, `min_region_area=100`, `dilate_radius=3`, `min_component_size=50`, `mask_suffix=".tif"`, `visualize=false`, and `random_state=null`. Omitted constructor defaults are `target_scale=1200`, `auto_scale_params=true`, and `full_image_mode=false`.

| View | Differentiating channel rule | Constructor compatibility |
|---|---|---|
| G0 | `do_not_warp_channels=[0,1]` | Yes |
| G1 | no include/exclude list | Yes |
| G2 | `do_warp_channels=[2]`, `do_not_warp_channels=[0,1]` | Yes |

Randomness is not frozen:

- `random_state` is `null` in all three named run settings.
- The class calls `np.random.seed(random_state)` only for a non-null state; otherwise probability draws, permutations, angles, and normal draws use global NumPy state.
- `sample_idx` does not seed the warp. Its only operational use is to suffix an optional visualization filename.
- Direct run metadata also records `sampling_seed: null` with `sampling_strategy: "hash_modulo"`; that is input sampling metadata, not a warp seed schedule.
- No per-document/per-view seed mapping, initial global RNG state, worker-order record, NumPy/runtime lock, or historical rendered-image SHA-256 was found.

The historical configured render root is absent. A runtime import probe also could not import the historical checkout in the current environment because `tqdm` is unavailable; the plain rerun produced exactly `ModuleNotFoundError: No module named 'tqdm'`. No dependency was installed. This does not undermine the source-level compatibility finding, but it is additional evidence that an exact historical runtime is not frozen here.

## 3. Can all frozen U/P/G definitions be rendered reproducibly?

**No.** Source identity passes, but all-nine render reproducibility is blocked.

The source-manifest check produced these exact results against `SOURCE_IMAGE_ROOT`:

```text
ROWS	622
UNIQUE_DOC_IDS	622
UNIQUE_RELATIVE_FILENAMES	622
UNIQUE_MANIFEST_HASHES	622
MISSING	0
SIZE_MISMATCH	0
HASH_MISMATCH	0
COLLECTION_SHA256	c1c1bd78585d34da500d94cb4c838cdcd664f9d2f19615158d4e312c29afd769
DIRECT_JPG_COUNT	622
```

That proves source linkage only.

| Views | Recoverable facts | Precise blocker |
|---|---|---|
| U0/U1/U2 | Original source JPEG bytes and hashes; U members must be byte-identical to one another | The matrix defines them after a route-required transport conversion, but no single executable transport/codec rule and payload hash is frozen in repository code. Route prose differs by provider. |
| P0/P1/P2 | IDs, dictionaries, source order, and historical pipeline position | Exact `granular_shift` implementation and manager input adapter are absent; no render hashes exist. |
| G0/G1/G2 | Active class, mask rule, dictionaries, defaults, config order, and source/mask stem linkage | No historical/per-view seeds or hashes; configured outputs are absent; resize/input semantics and the pure-warp projection are not historically equivalent to the ranked compound runs. |

There is no exact command/code path that consumes the verified 622-row source manifest and emits all nine frozen views. `generate_variants.py` is not such a path: it reads a different configuration key, depends on the incomplete registry, does not define the route payload conversion, and does not write a source-to-render hash manifest.

A future portable render manifest would need, at minimum, one row per `(doc_id, view_id)` with source relative name and SHA-256; mask logical name and SHA-256 where applicable; canonical transform ID/JSON and its hash; exact renderer and adapter hashes; deterministic seed or an explicit deterministic-no-randomness marker; runtime/dependency lock hash; pre-transport codec/options and rendered-image SHA-256; route transport rule/version; final payload SHA-256; dimensions/mode; and status. U0/U1/U2 must share the same final payload hash. Such an artifact must be generated from actual rendered bytes and independently rehashed. Because those bytes cannot presently be justified, no manifest or hashes were fabricated in this audit.

## 4. Existing manifests, hashes, seeds, and route transport

No safe render manifest already exists in the inspected repository or named direct run metadata.

- `config/source_image_manifest.csv` hashes the 622 **source JPEGs**, not U/P/G renders. Its `sha256` column must not be relabeled as rendered-image hashes.
- `src/icdar_tta/lineage.py` requires `source_image_hash`; it has no required rendered-image hash or payload hash field. `src/icdar_tta/schema.py` has an optional generic `image_hash`, but no populated render table uses it.
- The four named direct `processed_files.txt` ledgers contain 1,841, 1,235, 1,230, and 1,235 lines respectively. Their inspected first/last entries are source-image paths. Direct metadata searches found no SHA-256, render hash, or transformed-image path. These are source-path processing ledgers, not render manifests.
- The only named Grid random state is null. The only direct `sampling_seed` is also null and concerns hash-modulo input sampling.
- `ROUTE_AUDIT.md` describes prior external routes. For example, its Qwen route uses longest-side 1,280, RGB, Lanczos, JPEG quality 85, and inline base64, while Gemini route prose describes inline local JPEG bytes. Those descriptions are not one common, executable, version-locked U0 transport rule in the inspected repository, and no payload hashes exist.
- The official PA release checkout contains release verification and two representative originals in its landing-page tree, not historical augmentations, seeds, or render hashes.
- `HISTORICAL_RENDER_ROOT` does not exist at the exact path resolved from the active WARP config.

## 5. Pure-warp G0–G2 projection

The evidence is sufficient to put a **narrow, prospective design decision** to the project owner: the exact top-three v4 experiment IDs, parameter dictionaries, active class wiring, and historical compound-pipeline ranking are all identified and hashed. This makes G0–G2 a traceable proposed transfer projection.

The evidence is **not** sufficient to call pure-warp G0–G2 a historically validated ablation or to accept it automatically. Every ranked historical Grid row was evaluated as resize-to-1,504 → warp → one of five Pad variants. Removing the Pad stage—and potentially changing the resize/input rule—changes the tested intervention. There are no pure-warp historical render hashes or outcomes that isolate this projection.

Project-owner acceptance, if granted, should therefore state that G0–G2 are new predeclared pure-warp projections of historically ranked dictionaries, not reproductions of the ranked historical images. That acceptance would address experimental scope only; it would not resolve the missing deterministic renderer, seed, transport, and render-hash gates.

## Exact unresolved items

1. Named source and hash for the historical `granular_shift` implementation.
2. Historical manager adapter defining Pad behavior and `resize_mode: max_dimension` input semantics.
3. Explicit decision whether the prospective G views retain resize-to-1,504 before warp.
4. Deterministic per-document/per-view Grid seed schedule, or historical rendered bytes/hashes that make seeds unnecessary.
5. Frozen runtime/dependency versions and deterministic worker/RNG behavior.
6. Surviving historical transformed images or a newly accepted renderer capable of producing actual bytes.
7. One executable, route-specific transport conversion per model, including codec/options and final payload hashes; U0/U1/U2 byte identity must be proven.
8. A generated and independently verified source/mask/render/payload manifest covering 622 × 9 = 5,598 view rows.
9. Project-owner acceptance of the prospective pure-warp scope and its non-equivalence to historical compound runs.

## Gate recommendation

**Keep the render-lineage and live-call gates CLOSED.** Do not submit any provider request and do not claim that all nine views render until a reviewed generator can consume the 622-source manifest, exact mask set, frozen transform definitions, deterministic seed schedule, and frozen transport rules; produce 5,598 actual view records; and pass independent source/render/payload hash verification.

Recovery of a genuinely historical Pad source or historical render bytes would be preferred. If that is impossible, a newly implemented Pad renderer and seed schedule must be labeled a prospective replication choice, approved by the project owner, and tested rather than described as exact historical recovery.

## Validation

All validation was offline. Commands were run from the repository root. RTK-wrapped commands reported the exit status and streams shown below.

1. **Compileall**

   Command:

   ```text
   rtk env PYTHONPYCACHEPREFIX=/tmp/icdar_tta_compileall python3 -m compileall -q src scripts tests
   ```

   Outcome: exit status `0`; stdout empty; stderr empty.

2. **Complete 158-test suite**

   The canonical pytest-shaped attempt was made first:

   ```text
   rtk env PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -p no:cacheprovider
   ```

   It exited `1` with exact stderr `/usr/bin/python3: No module named pytest`. As required after an RTK-wrapped failure, the command was rerun plainly:

   ```text
   PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -p no:cacheprovider
   ```

   It also exited `1` with exact stderr `/usr/bin/python3: No module named pytest`. No dependency was installed. A source scan found zero pytest-specific API uses, so the same complete `unittest` suite was run directly:

   ```text
   rtk env PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -q
   ```

   Outcome: exit status `0`; exact result:

   ```text
   ----------------------------------------------------------------------
   Ran 158 tests in 2.181s

   OK
   ```

3. **Both-manifest validator**

   Command:

   ```text
   rtk env PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 python3 -m icdar_tta.validate --portable-manifest config/data_manifest.yaml --manifest config/data_manifest.local.yaml
   ```

   Outcome: exit status `0`; exact output:

   ```text
   [PASS] self_check.normalize: normalize_field/is_exact_match/character_error_rate OK
   [PASS] self_check.parser: strict PA v1.49 44-field success, age exception, repair audit, and failure paths OK
   [PASS] self_check.consensus: progressive_consensus deterministic OK ('Mary')
   [PASS] manifest.portable.secrets_and_shape: path=config/data_manifest.yaml errors=[] warnings=[]
   [PASS] manifest.local.shape: path=config/data_manifest.local.yaml errors=[]
   [PASS] field_table.provided: no --field-table path given; skipping schema validation (documented data gate)

   Overall: PASS (0 hard failure(s))
   ```

4. **Direct YAML safe parse**

   Command: `rtk python3` with an inline `yaml.safe_load` loop over exactly `config/data_manifest.yaml` and `config/data_manifest.local.yaml`.

   Outcome: exit status `0`; exact output:

   ```text
   config/data_manifest.yaml	PARSED	top_type=dict	schema_version=1	source_keys=15
   config/data_manifest.local.yaml	PARSED	top_type=dict	schema_version=1	source_keys=12
   ```

5. **Owned-artifact redaction and whitespace scan**

   Command: `rtk python3` with an inline scanner over exactly `local_agent/RENDER_LINEAGE_AUDIT.md` for WSL absolute paths, Windows absolute paths, UNC paths, credential-like terms, private named roots, and trailing whitespace.

   Initial outcome before inserting this validation section: exit status `0`; exact output:

   ```text
   wsl_absolute_path	0
   windows_absolute_path	0
   unc_path	0
   credential_term	0
   private_named_root	0
   trailing_whitespace_lines	0
   REDACTION_SCAN	PASS
   ```

   The same scan is rerun after this insertion; the final result is recorded below.

6. **Git whitespace check**

   Command:

   ```text
   rtk git diff --check
   ```

   Initial outcome before inserting this validation section: exit status `0`; no diagnostic output. The same command is rerun after this insertion; the final result is recorded below.

### Final artifact-sensitive recheck

After inserting the validation record, the owned-artifact scan was rerun with assignment-shaped secret checks to avoid treating this report's descriptive validation terminology as a secret. It exited `0`:

```text
wsl_absolute_path	0
windows_absolute_path	0
unc_path	0
secret_assignment	0
private_named_root	0
trailing_whitespace_lines	0
REDACTION_SCAN	PASS
```

`rtk git diff --check` was also rerun and exited `0` with no diagnostic output.
