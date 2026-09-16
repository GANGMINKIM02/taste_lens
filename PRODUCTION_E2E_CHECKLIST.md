# Production E2E Checklist — PRD v4.3

Run this after GitHub push, Vercel import, Supabase setup, image upload, and Upstage key configuration.

## 1. Deployment

- [ ] GitHub `main` pushed
- [ ] Vercel project linked to repository root
- [ ] Next.js home loads at `/`
- [ ] FastAPI health returns 200 at `/api/health`
- [ ] `/api/health` reports Supabase configured
- [ ] `/api/health` reports Upstage configured

## 2. Supabase

- [ ] `supabase/schema.sql` applied
- [ ] Storage bucket `taste-lens-assets` exists and is public for demo assets
- [ ] 70 Foods seeded
- [ ] 41 Restaurants seeded
- [ ] 210–250 RestaurantMenus seeded
- [ ] Image URL fields are populated

## 3. Images

- [ ] 70 Food WebP assets uploaded
- [ ] 41 Restaurant WebP assets uploaded
- [ ] 100–150 Menu unique WebP assets uploaded
- [ ] No placeholder is visible on the demo critical path
- [ ] Same Restaurant has no repeated Menu image
- [ ] Critical-path images are perceived as unique

## 4. User Journey

- [ ] New user created
- [ ] Pairwise Q1–Q6 coverage phase completes
- [ ] Pairwise Q7–Q10 adaptive phase completes
- [ ] `U_base` saved with vector version 1
- [ ] Auto Top-5 respects max 2 Foods per Category
- [ ] Category recommendation works as candidate filter
- [ ] Place/Time/Weather context produces `U_current`
- [ ] Food → Restaurant flow works
- [ ] Restaurant → Menu flow works
- [ ] Seller Menu order is preserved
- [ ] Menu-level Taste Match appears

## 5. Learning

- [ ] Normal order applies LR .05
- [ ] Reorder applies LR .08
- [ ] Order snapshot saves before/after vectors and versions
- [ ] Completed order appears in Order History
- [ ] Review submission calls Solar Pro 4
- [ ] Rating does not directly change Taste Vector
- [ ] Menu Taste claims create `review_evidence`
- [ ] Explicit User Preference with confidence >= .75 uses LR .02
- [ ] Failed Solar call sets Review status `failed`
- [ ] Failed Review can retry using the same `review_id`
- [ ] Review/Menu/User learning is not applied twice

## 6. Recommendation Logging

- [ ] Recommendation snapshot saved
- [ ] `selected_food_id` updated
- [ ] `selected_restaurant_id` updated
- [ ] `selected_restaurant_menu_id` updated
- [ ] Vector version is saved with recommendation

## Acceptance

```text
Frontend Build: PASS / FAIL
FastAPI: PASS / FAIL
Supabase PostgreSQL: PASS / FAIL
Supabase Storage: PASS / FAIL
Open-Meteo: PASS / FAIL
Solar Pro 4: PASS / FAIL
Pairwise: PASS / FAIL
Recommendation: PASS / FAIL
Order Learning: PASS / FAIL
Review Learning: PASS / FAIL
Image UX: PASS / FAIL
Full E2E: PASS / FAIL
```
