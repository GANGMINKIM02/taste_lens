#!/usr/bin/env python3
"""Build the complete PRD v4.3 image-generation manifest. No runtime generation is used."""
import csv,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from backend.app.seed_supabase import make,menu_variant_count

foods,restaurants,menus=make()
rows=[]
for f in foods:
    rows.append({
      'asset_type':'food','asset_key':f['food_id'],'target_path':f"foods/{f['food_id']}.webp",'width':800,'height':600,
      'prompt':f"Photorealistic Korean delivery-app food photography of {f['name']}. Single finished dish, appetizing realistic plating, 45-degree camera angle, natural restaurant lighting, neutral tabletop, no text, no logos, no watermark, no people, high detail, consistent commercial food photography style."})
for r in restaurants:
    rows.append({
      'asset_type':'restaurant','asset_key':r['restaurant_id'],'target_path':f"restaurants/{r['restaurant_id']}.webp",'width':1200,'height':800,
      'prompt':f"Photorealistic representative image for a Korean delivery restaurant named {r['name']}, category {r['category']}, type {r['restaurant_type']}. Distinct believable restaurant interior or storefront, warm commercial photography, no readable brand text, no logos, no watermark, no people in close-up."})
# Generate the exact 120-menu-image pool defined by seed_supabase.menu_variant_count.
for f in foods:
    for variant in range(1,menu_variant_count(f)+1):
      composition=['close-up hero bowl','three-quarter plated dish','top-down delivery presentation','table-level restaurant serving'][((variant-1)%4)]
      rows.append({
        'asset_type':'menu','asset_key':f"{f['food_id']}-v{variant:02d}",'target_path':f"menus/{f['food_id']}-v{variant:02d}.webp",'width':600,'height':450,
        'prompt':f"Photorealistic menu photography of {f['name']} for a Korean food delivery app, {composition}, visibly distinct from other variants of the same dish, realistic restaurant portion, appetizing texture, natural lighting, no text, no logos, no watermark, no people."})
out=ROOT/'assets'/'image_manifest.csv';out.parent.mkdir(parents=True,exist_ok=True)
with out.open('w',newline='',encoding='utf-8-sig') as fh:
    w=csv.DictWriter(fh,fieldnames=['asset_type','asset_key','target_path','width','height','prompt']);w.writeheader();w.writerows(rows)
print({'manifest':str(out),'total':len(rows),'food':sum(r['asset_type']=='food' for r in rows),'restaurant':sum(r['asset_type']=='restaurant' for r in rows),'menu':sum(r['asset_type']=='menu' for r in rows)})
