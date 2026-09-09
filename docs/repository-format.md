# Repository format

`index.json` is the machine-readable root. `Packages` and `Packages.gz` are generated package indexes. `SHA256SUMS` covers distributable metadata and package artifacts. Device profiles live below `devices/<model>/device.json`.

Package metadata must include name, version, architecture, platform, dependencies, description, download path, size, SHA-256, source reference, and compatibility.
## Upstream history imports

Historical third-party source states are recorded under metadata/upstream/.
Each entry records the exact upstream commit, source path, size and SHA-256.
These records are provenance data only; they are not treated as installable OPKG/IPK releases until a Fritz.Wulf package definition, compatibility profile and reproducible build exist.

The YourFritz import currently uses metadata/upstream/yourfritz-history.json and preserves older source states from PeterPawn/YourFritz without rewriting upstream history.

## Fritz.Wulf package-manager release sync

`Fritz-Wulf/fw` releases are synchronized by `scripts/sync_fw_releases.py`.
The sync accepts only semantic `vX.Y.Z` release tags with exactly one matching
`fw-X.Y.Z.tar.gz` asset, a GitHub-provided SHA-256 digest, a positive size, and
an exact tag-to-commit resolution. Existing versions are immutable: a mismatch
in artifact path, size, digest, source tag, or source commit aborts the sync.

`.github/workflows/sync-fw-releases.yml` polls hourly and can also be started
manually. New releases are downloaded into `packages/fritzwulf/fw/<version>/`,
then `Packages`, `Packages.gz`, `index.json`, and `SHA256SUMS` are rebuilt and
validated. The workflow never pushes generated changes directly to `main`; it
opens an automation branch and pull request so the normal validation gate still
applies. GitHub Pages publishes the new version only after that PR is merged.
## Device targets

Every package entry carries a machine-readable `devices` array. `fw` releases currently target `3270`, `7490`, `7530`, and `7590`; historical source-only snapshots use an empty array. The generated `Packages` feed exposes the same data as `X-Fritz-Wulf-Devices`, using `none` for an empty target set. Clients must not infer device compatibility from the free-text `compatibility` field.
