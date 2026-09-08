# Repository format

`index.json` is the machine-readable root. `Packages` and `Packages.gz` are generated package indexes. `SHA256SUMS` covers distributable metadata and package artifacts. Device profiles live below `devices/<model>/device.json`.

Package metadata must include name, version, architecture, platform, dependencies, description, download path, size, SHA-256, source reference, and compatibility.
## Upstream history imports

Historical third-party source states are recorded under metadata/upstream/.
Each entry records the exact upstream commit, source path, size and SHA-256.
These records are provenance data only; they are not treated as installable OPKG/IPK releases until a Fritz.Wulf package definition, compatibility profile and reproducible build exist.

The YourFritz import currently uses metadata/upstream/yourfritz-history.json and preserves older source states from PeterPawn/YourFritz without rewriting upstream history.
