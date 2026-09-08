#!/usr/bin/env python3
from pathlib import Path
import gzip, hashlib, json, sys
root=Path(__file__).resolve().parents[1]
errors=[]
idx=json.loads((root/'index.json').read_text())
if idx.get('format_version') != 1: errors.append('unsupported index format')
for model in idx.get('devices',[]):
    p=root/'devices'/model/'device.json'
    if not p.is_file(): errors.append(f'missing device profile: {model}')
    else:
        d=json.loads(p.read_text())
        if d.get('verification') not in {'VERIFIED','HISTORICAL VERIFIED','INFERRED','UNKNOWN'}: errors.append(f'invalid verification: {model}')
with gzip.open(root/'Packages.gz','rb') as fh:
    if fh.read() != (root/'Packages').read_bytes(): errors.append('Packages.gz mismatch')
for line in (root/'SHA256SUMS').read_text().splitlines():
    digest, rel=line.split('  ',1); p=root/rel
    if not p.is_file(): errors.append(f'missing checksummed file: {rel}')
    elif hashlib.sha256(p.read_bytes()).hexdigest()!=digest: errors.append(f'checksum mismatch: {rel}')
if errors:
    print('\n'.join('ERROR: '+e for e in errors)); sys.exit(1)
print('repository validation: OK')
