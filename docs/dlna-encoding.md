# DLNA encoding compatibility

The historically verified FRITZ!Box 7490 / FRITZ!OS 07.62 issue is an AVM `libexif.so.12.3.4` UTF-16LE to UTF-8 conversion defect affecting media metadata exposed to DLNA clients such as the Onkyo TX-NR696.

## Reconstructed source

The historical Fritz.Wulf patcher and converter source are preserved verbatim under `tools/7490/dlna/`. `metadata.json` records their source hashes plus the exact original, generated, patched-slot and patched-library SHA-256 contracts. The public repository does **not** redistribute AVM `libexif.so.12.3.4` or any other vendor binary.

The patcher accepts only the known original full-file and slot hashes, detects the known patched state, rejects unknown/tampered binaries, compiles the replacement with the MIPS/uClibc target toolchain, rejects `.text` relocations, and atomically preserves file mode during replacement.

## Encoding behavior

The converter reads UTF-16LE on the big-endian MIPS target, emits UTF-8 for BMP code points and valid surrogate pairs, maps isolated surrogates to U+FFFD, respects the output boundary, and always NUL-terminates when `outlen` is non-zero. Regression coverage must include ASCII, umlauts, ß, accents, non-Latin text, emoji, valid surrogate pairs, isolated surrogates, and boundary behavior.

The next hardware/build integration step is to compile this source with the pinned 7490 toolchain and exercise it against the known original AVM library inside a controlled firmware build; no production box is modified by repository tests.
