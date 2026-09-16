# GitHub + Vercel Deployment

## Target architecture

```text
GitHub repository
      ↓
Vercel project
  ├─ Next.js frontend       /
  └─ FastAPI Python runtime /api/*
            ↓
       Supabase PostgreSQL / Storage
            ↓
       Upstage Solar Pro 4
            ↓
       Open-Meteo
```

The app is intentionally a **single GitHub repository and a single Vercel project**. `api/index.py` is the Vercel FastAPI entrypoint and mounts the core backend at `/api`.

## 1. GitHub

Create an empty GitHub repository, then from this project root:

```bash
git init
git add .
git commit -m "Taste Lens MVP v4.3"
git branch -M main
git remote add origin <YOUR_GITHUB_REPOSITORY_URL>
git push -u origin main
```

Never commit `.env`, `.env.local`, Supabase secret keys, or Upstage API keys.

## 2. Vercel import

1. Vercel → Add New → Project.
2. Import the GitHub repository.
3. Framework Preset: Next.js (auto-detected).
4. Project Root: repository root.
5. Do **not** set a separate `web/` or `backend/` root.

Vercel deploys the root Next.js app and `api/index.py` Python function together.


## Python dependency packaging

Vercel reads the root `pyproject.toml` for the Python runtime. `requirements.txt` is kept for local development and GitHub CI.

## 3. Vercel environment variables

Add these in Project Settings → Environment Variables.

### Required

```env
SUPABASE_URL=https://YOUR_PROJECT.supabase.co
SUPABASE_SECRET_KEY=YOUR_SUPABASE_SECRET_KEY
SUPABASE_ASSET_BUCKET=taste-lens-assets
UPSTAGE_API_KEY=YOUR_UPSTAGE_API_KEY
UPSTAGE_API_BASE_URL=https://api.upstage.ai/v1
UPSTAGE_MODEL=solar-pro4
OPEN_METEO_ENABLED=true
NEXT_PUBLIC_API_BASE_URL=/api
```

### Optional

```env
CORS_ORIGINS=http://localhost:3000
```

`SUPABASE_SECRET_KEY` and `UPSTAGE_API_KEY` are server-only secrets. Never prefix either with `NEXT_PUBLIC_`.

## 4. Supabase before production deploy

1. Run `supabase/schema.sql` in Supabase SQL Editor.
2. Pre-generate image assets using `assets/image_manifest.csv`.
3. Optimize them with `python scripts/optimize_images.py`.
4. Upload them with `python scripts/upload_assets.py`.
5. Seed database with `python -m backend.app.seed_supabase`.

Images are generated **before runtime**, stored in Supabase Storage, and referenced by URL from PostgreSQL.

## 5. Local parity check

Recommended:

```bash
npm install
pip install -r requirements.txt
npm install -g vercel
vercel link
vercel dev
```

Then verify:

```text
http://localhost:3000/
http://localhost:3000/api/health
```

Alternative two-process development:

```bash
uvicorn backend.app.main:app --reload --port 8000
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000 npm run dev
```

## 6. Production verification

After Vercel deployment:

```text
https://YOUR_PROJECT.vercel.app/
https://YOUR_PROJECT.vercel.app/api/health
https://YOUR_PROJECT.vercel.app/api/v1/assets/status
```

`/api/health` should report Supabase and Upstage as configured, and runtime image generation as disabled.

## 7. GitHub CI

`.github/workflows/ci.yml` validates Python tests, image manifest constraints, Python compilation, and the Next.js build on push/PR.
