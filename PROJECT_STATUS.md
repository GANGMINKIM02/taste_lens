# Taste Lens PRD v4.3 — Project Status

This ZIP is the PRD v4.3 codebase and deployment package.

## Offline-verified in this package

- FastAPI/Python compile
- Backend unit tests
- 70 Food seed
- 41 Restaurant seed
- 241 RestaurantMenu seed
- Food >= 3 Restaurant constraint
- Korean Food >= 4 Restaurant constraint
- 231-row image-generation manifest
- 120 unique RestaurantMenu image pool mapping
- Vercel FastAPI gateway `/api/health`
- Canonical environment-variable names
- No runtime image generation
- Next.js `Image` component with lazy loading/fallback
- GitHub Actions CI definition
- GitHub → Vercel deployment documentation

## Requires external environment for live E2E

The following cannot be truthfully marked PASS until real credentials/assets are supplied:

1. Supabase PostgreSQL live read/write
2. Supabase Storage upload and live image rendering
3. Upstage Solar Pro 4 live review analysis
4. Open-Meteo network request in the deployed environment
5. Vercel production build/deploy
6. Full production E2E user journey

## Required server-side secrets

```env
SUPABASE_URL=
SUPABASE_SECRET_KEY=
SUPABASE_ASSET_BUCKET=taste-lens-assets
UPSTAGE_API_KEY=
UPSTAGE_API_BASE_URL=https://api.upstage.ai/v1
UPSTAGE_MODEL=solar-pro4
OPEN_METEO_ENABLED=true
CORS_ORIGINS=http://localhost:3000
```

Frontend:

```env
# local separate-process development
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000

# Vercel production
NEXT_PUBLIC_API_BASE_URL=/api
```

## Image assets

The ZIP contains the complete 231-row generation manifest and asset pipeline, but not 231 fabricated placeholder photographs. Production images must be generated from `assets/image_manifest.csv`, optimized to WebP, and uploaded to Supabase Storage before production E2E.
