# Historical YourFritz sources

Fritz.Wulf preserves verified historical source snapshots derived from the public
`PeterPawn/YourFritz` Git history.

The initial migration covers eight script-oriented components and 240 unique
source states. Every snapshot is stored byte-for-byte in this repository and is
identified by its upstream commit, original path, date, size and SHA-256 digest.

These entries use `git-YYYYMMDD-<commit>` versions when upstream did not publish
a semantic package version for that state. They are marked
`installable: false`, `platform: source-snapshot` and
`compatibility: historical-source-only`.

This is deliberate: a Git state is not automatically a tested OPKG/IPK release.
Installable Fritz.Wulf packages are promoted separately only after dependencies,
target ABI, installation layout and runtime behavior have been verified.

The authoritative provenance inventory is
`metadata/upstream/yourfritz-history.json`; generated repository metadata lives
in `metadata/packages/yourfritz-source.json`.
