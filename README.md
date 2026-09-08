# Fritz.Wulf Repository

Fritz.Wulf is a device-aware Freetz-NG extension and package platform. This repository is the public package source and GitHub Pages feed for supported FRITZ!Box profiles.

## Status

Initial repository foundation. Compatibility is declared per device profile; no firmware image is assumed compatible by product family name alone.

## Public feed

`https://fritz-wulf.github.io/repo/`

## CLI

The planned entry points `fritzwulf`, `fwulf`, and `fw` target the same runtime/package layer. Runtime/package updates are separate from firmware flashing.

## Security

Repository metadata and published artifacts are checksum-validated. Clients must fail closed on checksum or signature failures. Never publish credentials, private keys, private build infrastructure, or unknown-provenance binaries.
