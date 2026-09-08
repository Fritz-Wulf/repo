# DLNA encoding compatibility

The verified FRITZ!Box 7490 / FRITZ!OS 07.62 issue is an AVM `libexif.so.12.3.4` UTF-16LE to UTF-8 conversion defect affecting media metadata exposed to DLNA clients such as the Onkyo TX-NR696.

The historical Fritz.Wulf build tree contains source `custom/wulf7490/wulf_utf16_to_utf8.c` and a fail-closed patcher `patch_avm_libexif_utf16.py`. It checks exact SHA-256 hashes for the original library and patched slot and refuses unknown binaries.

Regression coverage must include ASCII, umlauts, ß, accents, non-Latin text, emoji, valid surrogate pairs, isolated surrogates, and output-boundary behavior. This repository does not redistribute the AVM binary.
