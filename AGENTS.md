# AGENTS.md

Work on branches named `agent/<work-area>-YYYYMMDD`. Preserve existing changes and avoid destructive git commands.

Fritz.Wulf uses one shared runtime/package layer plus device-specific integration profiles and architecture/ABI-specific packages. Never infer firmware compatibility from model names alone.

BMAX-B6 is the historical FRITZ!Box 7490 build host. Do not migrate historical builds to another host without an explicit, documented decision.

Before real-hardware changes verify model, firmware, network path, backups, and recovery. Runtime installation must never implicitly flash firmware.

Do not commit secrets, credentials, private keys, `.env` files, agent scratchpads, internal-only URLs, or unredacted local build infrastructure.

Run `python3 scripts/build_repository.py` and `python3 scripts/validate_repository.py` before committing repository metadata changes.
