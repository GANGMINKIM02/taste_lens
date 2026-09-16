#!/usr/bin/env python3
"""Offline verification for Taste Lens PRD v4.3.

This intentionally avoids live Supabase/Upstage calls. It validates the project
shape, seed constraints, image manifest, canonical environment names and the
Vercel FastAPI gateway health endpoint.
"""
from pathlib import Path
import csv
import os
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

CANONICAL = {
    'SUPABASE_URL', 'SUPABASE_SECRET_KEY', 'SUPABASE_ASSET_BUCKET',
    'UPSTAGE_API_KEY', 'UPSTAGE_API_BASE_URL',
    'UPSTAGE_MODEL', 'OPEN_METEO_ENABLED', 'CORS_ORIGINS',
    'NEXT_PUBLIC_API_BASE_URL'
}
FORBIDDEN = {
    'SUPABASE_SERVICE_ROLE_KEY', 'SUPABASE_ANON_KEY', 'NEXT_PUBLIC_SUPABASE_URL',
    'NEXT_PUBLIC_SUPABASE_ANON_KEY', 'SOLAR_API_KEY', 'SOLAR_API_BASE_URL',
    'SOLAR_MODEL', 'UPSTAGE_SECRET_KEY'
}


def assert_true(value, message):
    if not value:
        raise AssertionError(message)


def main():
    from backend.app.seed_supabase import make
    foods, restaurants, menus = make()
    assert_true(len(foods) == 70, f'foods={len(foods)}')
    assert_true(len(restaurants) == 41, f'restaurants={len(restaurants)}')
    assert_true(210 <= len(menus) <= 250, f'menus={len(menus)}')
    assert_true(len({f['food_image_url'] for f in foods}) == 70, 'Food image URLs must be unique')
    assert_true(len({r['restaurant_image_url'] for r in restaurants}) == 41, 'Restaurant image URLs must be unique')
    assert_true(100 <= len({m['menu_image_url'] for m in menus}) <= 150, 'Menu unique pool out of PRD range')

    carriers = {f['food_id']: set() for f in foods}
    counts = {r['restaurant_id']: 0 for r in restaurants}
    food_map = {f['food_id']: f for f in foods}
    for m in menus:
        carriers[m['food_id']].add(m['restaurant_id'])
        counts[m['restaurant_id']] += 1
    assert_true(min(map(len, carriers.values())) >= 3, 'Every food must be sold by >=3 restaurants')
    korean = [len(carriers[f['food_id']]) for f in foods if f['category'] == '한식']
    assert_true(min(korean) >= 4, 'Korean foods must be sold by >=4 restaurants in this seed')
    assert_true(min(counts.values()) >= 4, 'Every restaurant must have >=4 menus')
    assert_true(any(f['category'] == '기타·글로벌' for f in foods), 'Canonical 기타·글로벌 category missing')

    manifest = ROOT / 'assets' / 'image_manifest.csv'
    rows = list(csv.DictReader(manifest.open(encoding='utf-8-sig')))
    assert_true(len(rows) == 231, f'manifest={len(rows)}')
    assert_true(len({r['target_path'] for r in rows}) == 231, 'Manifest target paths must be unique')

    env_text = (ROOT / '.env.example').read_text(encoding='utf-8') + '\n' + (ROOT / '.env.local.example').read_text(encoding='utf-8')
    for name in CANONICAL:
        assert_true(name in env_text, f'canonical env missing: {name}')
    project_text = '\n'.join(
        file.read_text(encoding='utf-8', errors='ignore')
        for file in ROOT.rglob('*')
        if file.is_file()
        and file != Path(__file__).resolve()
        and file.name != 'Taste Lens Final PRD v4.3.md'
        and file.suffix in {'.py','.ts','.tsx','.md','.yml','.yaml','.json','.example'}
        and 'node_modules' not in file.parts
    )
    for name in FORBIDDEN:
        assert_true(name not in project_text, f'forbidden env alias remains: {name}')
    assert_true('PRD v4.2' not in project_text, 'stale PRD v4.2 reference remains')
    assert_true((ROOT / 'Taste Lens Final PRD v4.3.md').exists(), 'PRD v4.3 file missing')
    assert_true('unoptimized' not in (ROOT/'components'/'SafeImage.tsx').read_text(encoding='utf-8'), 'Next Image optimization disabled')

    # No real credentials are needed for /api/health.
    from fastapi.testclient import TestClient
    from api.index import app
    client = TestClient(app)
    health = client.get('/api/health')
    assert_true(health.status_code == 200, f'/api/health={health.status_code}')
    payload = health.json()
    assert_true(payload.get('runtime_image_generation') is False, 'Runtime image generation must be disabled')

    print({
        'ok': True,
        'prd': 'v4.3',
        'foods': len(foods),
        'restaurants': len(restaurants),
        'restaurant_menus': len(menus),
        'manifest_assets': len(rows),
        'unique_menu_pool': len({m['menu_image_url'] for m in menus}),
        'api_health': health.status_code,
        'runtime_image_generation': payload.get('runtime_image_generation'),
    })

if __name__ == '__main__':
    main()
