#!/usr/bin/env python3
"""Upload pre-generated WebP assets to Supabase Storage. Images are never generated at runtime."""
import csv,os,sys
from pathlib import Path
from dotenv import load_dotenv
ROOT=Path(__file__).resolve().parents[1];load_dotenv(ROOT/'.env')
sys.path.insert(0,str(ROOT))
from backend.app.db import get_db
from backend.app.assets import BUCKET
manifest=ROOT/'assets'/'image_manifest.csv';assetroot=ROOT/'assets'/'generated'
db=get_db()
try:
    buckets=db.storage.list_buckets()
    names={getattr(b,'name',None) or (b.get('name') if isinstance(b,dict) else None) for b in buckets}
    if BUCKET not in names: db.storage.create_bucket(BUCKET,options={'public':True})
except Exception as e:
    print('Bucket create/list warning:',e)
count=0;missing=[]
with manifest.open(encoding='utf-8-sig') as fh:
  for r in csv.DictReader(fh):
    p=assetroot/r['target_path']
    if not p.exists():missing.append(r['target_path']);continue
    with p.open('rb') as f:
      db.storage.from_(BUCKET).upload(r['target_path'],f,file_options={'content-type':'image/webp','upsert':'true'})
    count+=1
print({'bucket':BUCKET,'uploaded':count,'missing':len(missing)})
if missing: raise SystemExit('Generate/optimize all manifest assets before upload.')
