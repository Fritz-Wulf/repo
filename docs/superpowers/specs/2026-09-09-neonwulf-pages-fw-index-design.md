# NeonWulf Pages + fw Index Design

## Goal

Create a coherent public Fritz.Wulf web and package-distribution surface across `https://fritz-wulf.github.io/`, `https://fritz-wulf.github.io/repo/`, and `https://fritz-wulf.github.io/repo/index.json`, while introducing `Fritz-Wulf/fw` as the package manager whose releases are represented in the same index.

## Architecture

The canonical package data remains in `Fritz-Wulf/repo`. `scripts/build_repository.py` generates `index.json`, `Packages`, `Packages.gz`, checksums, and a browser-friendly package catalog from declarative metadata. The `/repo/` page reads only `index.json`; it has no separate package database.

The organization root uses a dedicated public repository named `Fritz-Wulf/Fritz-Wulf.github.io`, because GitHub Pages organization-root sites require the `<org>.github.io` repository. It shares the NeonWulf design language but does not duplicate package metadata.

`Fritz-Wulf/fw` is a public repository. Its release metadata is imported into `Fritz-Wulf/repo` through machine-readable metadata and later CI automation; no release may overwrite an older version.

## Visual Contract

Use the verified visual principles from the existing Legion and Spinnennet gateways: midnight/anthracite surfaces, pink-purple-turquoise-mint accents, thin neon borders, glass panels, a perspective horizon grid, restrained scanlines, gradient wordmarks, monospaced metadata, and reduced-motion support.

Do not clone the reference pages literally. Fritz.Wulf gets its own wolf/package identity, stronger information hierarchy, and a catalog-first layout. Decorative motion stays subordinate to package discovery.

## Repository Catalog

Desktop: hero/status strip, search field, filter controls, sortable data table, package count, latest-update indicator, and package detail drawer/expanded row. Mobile: search and filter controls first, then stacked package cards preserving name/version/date/source/installability without hover.

Sorting must support at least name, version, date, architecture, source, size, and installability. Search covers package name, version, description, source reference, compatibility, and license.

Filters must support installable state, architecture, platform/source family, and device compatibility when present.
## Data Contract

Every package entry must retain existing required fields and may add `package_type`, `source`, `release_date`, `channel`, `devices`, `verification`, and `installable`. Historical YourFritz source snapshots remain `installable: false`; the browser must label them as historical source-only rather than implying they are OPKG packages.

`fw` versions are represented as ordinary versioned package records with a stable package name (`fw`), source repository `Fritz-Wulf/fw`, release/tag/commit provenance, download path, size, SHA-256, channel, and compatibility metadata.

## Root Site

The root page is a project gateway with links to Repository, Package Manager, Devices, Documentation, Security/Integrity, and GitHub. It shows current repository counts by fetching `/repo/index.json` client-side and degrades gracefully when the feed is unavailable.

## Accessibility and Performance

Essential package values are visible without hover. Keyboard users can focus headers, filters, package links, and detail controls. Search has an explicit label. Table headers expose sort state. `prefers-reduced-motion` disables parallax/orbit/lightning effects. No external fonts are required; no runtime framework is necessary.

## Testing

Use TDD for catalog behavior. Node's built-in test runner tests pure filtering/sorting/formatting helpers. Python repository tests verify schema/data integrity and generated-site references. A lightweight local HTTP smoke test verifies HTML, JS, CSS, and JSON resolve together.

## Release Safety

No automatic firmware flashing is introduced. No secrets, private host addresses, private keys, or internal device identifiers are published. Pages deploy only after repository validation passes. `fw` release ingestion must be additive and fail on duplicate name/version pairs or bad artifact hashes.