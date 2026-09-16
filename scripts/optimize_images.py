#!/usr/bin/env python3
"""Convert generated source images to PRD-recommended WebP sizes/quality."""
import csv
from pathlib import Path
from PIL import Image,ImageOps
ROOT=Path(__file__).resolve().parents[1]
manifest=ROOT/'assets'/'image_manifest.csv'; srcroot=ROOT/'assets'/'generated';
count=0;missing=[]
with manifest.open(encoding='utf-8-sig') as fh:
  for r in csv.DictReader(fh):
    target=srcroot/r['target_path']; stem=target.with_suffix('')
    candidates=[target,stem.with_suffix('.png'),stem.with_suffix('.jpg'),stem.with_suffix('.jpeg'),stem.with_suffix('.webp')]
    source=next((p for p in candidates if p.exists()),None)
    if not source: missing.append(r['target_path']);continue
    target.parent.mkdir(parents=True,exist_ok=True)
    im=Image.open(source).convert('RGB'); size=(int(r['width']),int(r['height']))
    im=ImageOps.fit(im,size,method=Image.Resampling.LANCZOS)
    im.save(target,'WEBP',quality=76,method=6)
    count+=1
print({'optimized':count,'missing':len(missing)})
if missing:
  print('Missing first 20:',*missing[:20],sep='\n- ')
