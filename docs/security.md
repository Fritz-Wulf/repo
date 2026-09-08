# Security

Published artifacts require provenance and SHA-256 verification. Signature support is required before the repository is declared production-ready. Clients must reject corrupted packages, wrong checksums, and invalid signatures.

Never publish passwords, tokens, private keys, `.env` files, private infrastructure data, or unknown-provenance binaries.
