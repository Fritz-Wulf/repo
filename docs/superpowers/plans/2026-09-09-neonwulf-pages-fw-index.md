# NeonWulf Pages + fw Index Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish a NeonWulf organization root site, a searchable/sortable package catalog, and a new `Fritz-Wulf/fw` package-manager repository whose versions feed the same `index.json`.

**Architecture:** `Fritz-Wulf/repo` owns package metadata and generated feed. Static JS renders `/repo/` from `index.json`. `Fritz-Wulf/Fritz-Wulf.github.io` owns the root gateway. `Fritz-Wulf/fw` owns package-manager code/releases and exports release metadata into the repository workflow.

**Tech Stack:** Python 3, vanilla HTML/CSS/ES modules, Node built-in test runner, GitHub Actions/Pages, POSIX shell for `fw` bootstrap.

**Spec:** `docs/superpowers/specs/2026-09-09-neonwulf-pages-fw-index-design.md`

## Global Constraints

- `index.json` is the single source of truth for package data.
- Historical source-only entries remain non-installable.
- No automatic firmware flashing.
- Preserve all old package versions; reject duplicate name/version pairs.
- Reduced-motion, keyboard, and mobile paths are first-class.
- No secrets or private infrastructure data in public repositories.

---

### Task 1: Package catalog behavior (TDD)

**Files:** create `assets/js/catalog-core.mjs`, `tests/catalog-core.test.mjs`; modify `index.html` and generated metadata only after tests fail correctly.

- [ ] Write tests for text search, multi-key sorting, installable filter, date fallback, and stable ordering.
- [ ] Run `node --test tests/catalog-core.test.mjs` and confirm RED because the module does not exist.
- [ ] Implement pure catalog helpers with no DOM dependency.
- [ ] Re-run Node tests and confirm GREEN.
- [ ] Build DOM integration around tested helpers; preserve URL query state for search/sort/filter.
### Task 2: NeonWulf repository UI

**Files:** create `assets/css/neonwulf.css`, `assets/js/catalog-app.mjs`; replace `index.html`; extend `tests/test_repository.py`.

- [ ] Add failing Python assertions for required asset references, accessible search label, sortable table hooks, and reduced-motion stylesheet rule.
- [ ] Run repository tests and confirm RED.
- [ ] Implement the responsive Retrowave/NeonWulf page using the Legion/Spinnennet principles without copying their page structure.
- [ ] Run Node and Python tests; validate generated repository files.
- [ ] Serve locally and smoke-test `/`, `/index.json`, CSS, and JS over HTTP.

### Task 3: Create `Fritz-Wulf/fw`

**Files:** new repository with `AGENTS.md`, `README.md`, `VERSION`, `bin/fw`, alias wrappers, `lib/fritzwulf/*`, tests, and CI.

- [ ] Create public GitHub repo and local checkout.
- [ ] Add failing tests for `version`, repository URL constant, aliases, `--json`, and rejection of non-installable package records.
- [ ] Implement the minimum read-only client: `version`, `update`, `search`, `list`, `info`, `device`, `doctor` without install/flash side effects.
- [ ] Run tests and shell syntax checks.
- [ ] Tag/release only after CI is green; record the release artifact metadata for repository ingestion.

### Task 4: Organization root site

**Files:** new `Fritz-Wulf/Fritz-Wulf.github.io` repository with `index.html`, `assets/css/neonwulf.css`, `assets/js/site.mjs`, and Pages workflow.

- [ ] Create the required organization-site repository.
- [ ] Implement the project gateway and fetch public counts from `/repo/index.json` with offline fallback.
- [ ] Add static validation for required links and accessibility landmarks.
- [ ] Push via feature branch/PR, verify Pages build, and confirm root URL returns the gateway.

### Task 5: fw release ingestion + end-to-end verification

**Files:** modify `metadata/packages/*`, `scripts/build_repository.py`, `scripts/validate_repository.py`, CI, and docs.

- [ ] Add a failing repository test proving an `fw` version must appear in both generated `index.json` and `Packages` with hash/provenance.
- [ ] Add declarative `fw` metadata and import helper.
- [ ] Rebuild repository artifacts and run full validation/tests.
- [ ] Push PR, require green CI, merge, and verify Pages URLs and package catalog behavior.
- [ ] Re-run all verification commands immediately before claiming completion.