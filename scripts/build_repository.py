#!/usr/bin/env python3
from pathlib import Path
import gzip, hashlib
root=Path(__file__).resolve().parents[1]
packages=root/'Packages'
packages.write_text('', encoding='utf-8')
with gzip.GzipFile(filename=str(root/'Packages.gz'), mode='wb', mtime=0) as fh:
    fh.write(packages.read_bytes())
include=['index.json','Packages','Packages.gz']
include += [str(p.relative_to(root)) for p in sorted((root/'devices').glob('*/device.json'))]
lines=[]
for rel in include:
    p=root/rel
    lines.append(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {rel}")
(root/'SHA256SUMS').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(f'built repository metadata for {len(include)} files')
