# PRD v4.3 implementation checklist

## Implemented in code

- 6-axis Taste Space: sweet, salty, sour, umami, spicy, nutty
- 70 Food seed
- Restaurant-first N:M dataset: 41 Restaurants, 241 RestaurantMenus
- Every Food >= 3 Restaurants; every Korean Food >= 4
- Pairwise onboarding 10 questions
  - Q1–Q6 coverage balancing
  - Q7–Q10 adaptive refinement
  - no repeated pair, food repeat constraints
  - beta 8, lambda .05, bounded coordinate descent steps
- `U_base` persisted in Supabase
- `U_current = clip(U_base + Delta_place + Delta_time + Delta_weather)`
- Place / Time / Weather reliability priors/scales from PRD
- Auto Top-5 with max 2 from same Category
- Category used as candidate filter, not Taste feature
- Food match / RestaurantMenu match equations
- Food → Restaurant → Menu discovery flow
- Seller menu order preserved
- Order LR .05 / Reorder LR .08
- Order snapshot/version logging
- Optional order impact UX
- Review flow from completed orders
- Solar Pro 4 strict structured review interpretation
- Rating separated from Taste learning
- Explicit preference + confidence >= .75 only for User review learning
- Review user LR .02
- Review evidence/status/idempotency fields
- Recommendation snapshots + selected Food/Restaurant/Menu logging
- Open-Meteo weather classification with rain priority, 28℃ hot, 8℃ cold
- Browser-local Time Segment passed to backend
- Supabase PostgreSQL persistence
- Supabase Storage production image architecture
- No runtime AI image generation
- 70 unique Food image paths
- 41 unique Restaurant image paths
- 120 unique RestaurantMenu image pool mapped to 241 menus
- Same Restaurant has no repeated menu image
- Korean Food comparison paths have >= 4 menu variants
- 231-row offline image-generation manifest
- WebP optimization script
- Supabase Storage upload script
- Local failure-only WebP fallback assets
- Next.js image component with fallback

## Requires external credentials / generated assets before final live E2E

- `SUPABASE_URL`
- `SUPABASE_SECRET_KEY`
- `UPSTAGE_API_KEY`
- 231 generated image files produced from `assets/image_manifest.csv`

Without those external values/assets, numeric/seed/image-mapping logic can be tested, but live Supabase CRUD, live Solar analysis and production image display cannot be honestly claimed as E2E verified.

## GitHub / Vercel deployment compliance

- Repository is structured for one GitHub repository.
- Vercel root hosts Next.js.
- `api/index.py` exposes FastAPI under `/api/*` on the same Vercel deployment.
- `NEXT_PUBLIC_API_BASE_URL=/api` uses same-origin production API routing.
- Server secrets use `SUPABASE_SECRET_KEY` and `UPSTAGE_API_KEY` only.
- Runtime image generation remains disabled; Supabase Storage serves pre-generated images.

## PRD v4.3 deployment/release additions

- GitHub `main` → Vercel production workflow documented
- One Vercel project: Next.js `/`, FastAPI `/api/*`
- Root `pyproject.toml` for Vercel Python dependency packaging
- Canonical `SUPABASE_SECRET_KEY` and `UPSTAGE_API_KEY` names
- `OPEN_METEO_ENABLED` is enforced by the weather endpoint
- Failed Solar review analysis can retry using the same `review_id`
- Next.js Image optimization is enabled (no `unoptimized` flag)
- Production E2E checklist included
