# DLNA encoding compatibility

The historically verified FRITZ!Box 7490 / FRITZ!OS 07.62 issue is an AVM `libexif.so.12.3.4` UTF-16LE to UTF-8 conversion defect affecting media metadata exposed to DLNA clients such as the Onkyo TX-NR696.

## Reconstructed source

The historical Fritz.Wulf patcher and converter source are preserved verbatim under `tools/7490/dlna/`. `metadata.json` records their source hashes plus the exact original, generated, patched-slot and patched-library SHA-256 contracts. The public repository does **not** redistribute AVM `libexif.so.12.3.4` or any other vendor binary.

The patcher accepts only the known original full-file and slot hashes, detects the known patched state, rejects unknown/tampered binaries, compiles the replacement with the MIPS/uClibc target toolchain, rejects `.text` relocations, and atomically preserves file mode during replacement.

## Freetz build integration

`stage_into_freetz.py` is plan-only by default. It requires `FREETZ_TYPE_7490=y`, `FREETZ_INFO_BOXTYPE=7490` and `FREETZ_INFO_FIRMWAREVERSION=07.62` before it will stage anything. `--apply` copies only the four public source/metadata files to `custom/wulf7490/` and inserts one idempotent `FRITZWULF_7490_DLNA_UTF16` call into `fwmod_custom`.

```sh
python3 tools/7490/dlna/stage_into_freetz.py --freetz-root /path/to/freetz-ng
python3 tools/7490/dlna/stage_into_freetz.py --freetz-root /path/to/freetz-ng --apply
```

During a Freetz build, the staged `freetz_hook.py` checks the exact target hash before delegating to the historical patcher. Unknown firmware/library combinations fail closed. A patched target is detected idempotently. No router is contacted or flashed by these tools.

## Encoding behavior

The converter reads UTF-16LE on the big-endian MIPS target, emits UTF-8 for BMP code points and valid surrogate pairs, maps isolated surrogates to U+FFFD, respects the output boundary, and always NUL-terminates when `outlen` is non-zero. CI exercises ASCII, umlauts, ß, accents, non-Latin text, emoji, valid surrogate pairs, isolated surrogates and boundary behavior.
