#!/usr/bin/env python3
import csv,sys
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from backend.app.seed_supabase import make
foods,restaurants,menus=make(); manifest=ROOT/'assets'/'image_manifest.csv'
rows=list(csv.DictReader(manifest.open(encoding='utf-8-sig')))
assert len(foods)==70 and len(restaurants)==41 and 210<=len(menus)<=250
assert Counter(r['asset_type'] for r in rows)=={'food':70,'restaurant':41,'menu':120}
assert len({f['food_image_url'] for f in foods})==70
assert len({r['restaurant_image_url'] for r in restaurants})==41
assert len({m['menu_image_url'] for m in menus})==120
# No image repeats within a single restaurant detail screen.
by_rest=defaultdict(list)
for m in menus:by_rest[m['restaurant_id']].append(m['menu_image_url'])
assert all(len(v)==len(set(v)) for v in by_rest.values())
# Korean foods have at least four distinct menu variants across their restaurant-comparison path.
by_food=defaultdict(list)
for m in menus:by_food[m['food_id']].append(m['menu_image_url'])
for f in foods:
  if f['category']=='한식': assert len(set(by_food[f['food_id']]))>=4
print({'ok':True,'foods':len(foods),'restaurants':len(restaurants),'menus':len(menus),'manifest_assets':len(rows),'unique_menu_pool':120})
