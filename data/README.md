# Data directory

This repository is **not** assumed to be the canonical storage location for the historical image corpus or large raw model-response trees.

## What should live here / in Git

Good candidates:

- public dataset index/metadata;
- portable manifests;
- small fixtures for unit tests;
- transform configuration tables;
- checksums/file indices;
- compact derived/aggregate tables needed for presentation charts, when release-safe.

## What should normally stay outside Git

- private/non-releasable archival images;
- huge transformed-image trees;
- bulk raw API response dumps if they are large or sensitive;
- machine scratch/cache directories;
- credentials/tokens;
- workstation-specific absolute paths.

Use `docs/DATA_CONTRACT.md` and `config/data_manifest.local.yaml` to connect local storage to repository code.
