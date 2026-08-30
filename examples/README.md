# Release-authorized sample data

This directory contains the two representative image/label examples from the
official Pennsylvania Death Records 622 release. They are included in that
release for public README/landing-page display and are copied here as a small,
release-authorized fixture for cloud-side inspection and smoke testing.

The full image corpus, masks, and raw model responses are not included. The
source release's `LICENSE.md` and `RELEASE_NOTES.md` remain the authority for
use of these examples and the underlying records.

Files:

- `samples/41381_1220705043_0549-04785.jpg`
- `samples/41381_1220705043_0567-00432.jpg`
- `example_labels.csv`

The two image bytes match the source release SHA-256 values recorded in
`config/source_image_manifest.csv`.
