# Taste Lens MVP — PRD v4.3

Taste Lens is a PRD-driven MVP implemented as a **single GitHub repository deployed to a single Vercel project**.

## Architecture

```text
Vercel
├─ Next.js / React                  /
└─ FastAPI                          /api/*
      ├─ Python numeric engine
      ├─ Upstage Solar Pro 4        review interpretation only
      ├─ Open-Meteo                 weather context
      └─ Supabase
           ├─ PostgreSQL
           └─ Storage               pre-generated WebP assets
```

Core principle: **Solar interprets. Python calculates.**

Runtime image generation is disabled. Food/restaurant/menu images are generated before deployment, optimized to WebP, uploaded to Supabase Storage, and referenced through DB URLs.

## Canonical environment variables

Use these exact names everywhere.

```env
SUPABASE_URL=
SUPABASE_SECRET_KEY=
SUPABASE_ASSET_BUCKET=taste-lens-assets

UPSTAGE_API_KEY=
UPSTAGE_API_BASE_URL=https://api.upstage.ai/v1
UPSTAGE_MODEL=solar-pro4

OPEN_METEO_ENABLED=true
CORS_ORIGINS=http://localhost:3000
NEXT_PUBLIC_API_BASE_URL=/api
```

Security:

- `SUPABASE_SECRET_KEY`: backend/Vercel server environment only.
- `UPSTAGE_API_KEY`: backend/Vercel server environment only.
- Never create `NEXT_PUBLIC_SUPABASE_SECRET_KEY` or `NEXT_PUBLIC_UPSTAGE_API_KEY`.
- `NEXT_PUBLIC_API_BASE_URL=/api` is safe because it contains no secret.

## Repository layout

```text
app/                       Next.js App Router
components/                UI components
lib/                       frontend API client
public/                    local failure-only fallback images
api/index.py               Vercel FastAPI entrypoint
backend/app/               core FastAPI application
backend/tests/             numeric / seed tests
supabase/schema.sql        PostgreSQL schema
assets/image_manifest.csv  231 pre-generation image jobs
scripts/                   image optimize/upload/validation
.github/workflows/ci.yml   GitHub CI
DEPLOYMENT.md              GitHub + Vercel deployment guide
```

## Image assets

PRD production target:

- Food: 70 unique images
- Restaurant: 41 unique representative images
- RestaurantMenu image pool: 120 unique images
- Total image generation jobs: 231
- Current generated RestaurantMenu rows: 241

Workflow:

```text
assets/image_manifest.csv
→ FLUX / Ideogram / equivalent generator (offline)
→ assets/generated/
→ python scripts/optimize_images.py
→ python scripts/upload_assets.py
→ Supabase Storage
→ python -m backend.app.seed_supabase
→ DB URL mapping
→ Next.js rendering
```

The production app never waits for an image-generation API call.

## Supabase setup

1. Create a Supabase project.
2. Run `supabase/schema.sql` in SQL Editor.
3. Put `SUPABASE_URL` and `SUPABASE_SECRET_KEY` in local `.env` or Vercel environment variables.
4. Generate/optimize/upload image assets.
5. Seed the DB:

```bash
python -m backend.app.seed_supabase
```

Expected seed constraints:

- foods: 70
- restaurants: 41
- restaurant_menus: 210–250 (currently 241)
- every Food sold by at least 3 Restaurants
- core Korean Food sold by at least 4 Restaurants
- every Restaurant has at least 4 Taste Lens menus

## Upstage Solar Pro 4

The review analyzer reads:

```env
UPSTAGE_API_KEY=
UPSTAGE_API_BASE_URL=https://api.upstage.ai/v1
UPSTAGE_MODEL=solar-pro4
```

Solar only extracts structured `menu_taste_claims` and `user_preference_claims`. Ranking, distance, context arithmetic, vector learning, and DB transactions remain Python logic.

## Local run — recommended Vercel parity

```bash
npm install
pip install -r requirements.txt / pyproject.toml
npm install -g vercel
vercel link
vercel dev
```

Open:

```text
http://localhost:3000
http://localhost:3000/api/health
```

## Local run — separate processes

Backend:

```bash
uvicorn backend.app.main:app --reload --port 8000
```

Frontend:

```bash
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000 npm run dev
```

## Verification

```bash
pytest -q backend/tests
python scripts/validate_assets.py
python -m compileall backend/app api scripts
npm install
npm run build
```

Actual Supabase + Upstage E2E requires valid external credentials.

## GitHub + Vercel

See `DEPLOYMENT.md`.

Production endpoints after deployment:

```text
https://YOUR_PROJECT.vercel.app/
https://YOUR_PROJECT.vercel.app/api/health
https://YOUR_PROJECT.vercel.app/api/v1/assets/status
```

## Implemented PRD journey

```text
Pairwise ×10
→ U_base
→ Home
→ Taste Lens
→ U_current (Place + Time + Weather)
→ Food recommendation
→ Restaurant comparison
→ Restaurant detail
→ Menu-level Taste Match
→ Order / Reorder learning
→ Order history
→ Review
→ Upstage Solar Pro 4 interpretation
→ RestaurantMenu learning
→ optional explicit User Preference learning
→ Next recommendation
```

## Final status / E2E

See `PROJECT_STATUS.md` for what is offline-verified and `PRODUCTION_E2E_CHECKLIST.md` for the live deployment acceptance test.
