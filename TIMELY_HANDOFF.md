# Timely AI / Solar Pro 4 — PRD v4.3 Handoff

이 ZIP은 PRD 수식·DB·Storage 구조를 기준으로 이미 분리되어 있습니다. Timely에 전체 ZIP을 한 번에 다시 설계시키지 말고 아래 순서로 검토합니다.

## 1. Numeric engine
Attach: `backend/app/engine.py`, `backend/app/context.py`, `backend/app/onboarding.py`

Prompt:
> Taste Lens PRD v4.3 numeric engine입니다. six-axis Taste Space, Pairwise beta=8, lambda=.05, bounded coordinate descent step sequence, Place/Time/Weather reliability formulas, Food/Menu distance equation을 변경하지 마세요. Solar는 numeric calculation을 수행하지 않습니다. import/runtime 오류와 코드 품질만 검토하고 complete replacement file을 반환하세요.

## 2. Supabase persistence
Attach: `backend/app/db.py`, `backend/app/main.py`, `supabase/schema.sql`

Prompt:
> Architecture는 Browser → Next.js → FastAPI → Supabase PostgreSQL/Storage입니다. local DB로 대체하지 마세요. users, user_profiles, onboarding_responses, orders, reviews, review_evidence, recommendations의 snapshot/version/idempotency를 유지하세요. Supabase Secret Key는 backend/Vercel server environment에만 둡니다. Recommendation의 selected_food_id / selected_restaurant_id / selected_restaurant_menu_id logging도 유지하세요.

## 3. Image pipeline
Attach: `backend/app/assets.py`, `backend/app/seed_supabase.py`, `scripts/*`, `assets/image_manifest.csv`

Prompt:
> PRD 이미지 전략을 유지하세요. 런타임 이미지 생성 API 호출을 절대 추가하지 마세요. 이미지 생성은 사전에 완료하고 Supabase Storage에 WebP로 저장하며 DB에는 URL만 저장합니다. Food 70 unique, Restaurant 41 unique, Menu pool 120 unique, 동일 Restaurant 내부 이미지 반복 금지, 한식 Food 비교 경로 최소 4 variants를 유지하세요. 이미지 provider를 바꾸더라도 target_path와 DB mapping을 깨지 마세요.

## 4. Solar review analysis
Attach: `backend/app/solar.py` and review endpoint in `backend/app/main.py`

Prompt:
> Solar Pro 4는 Review natural-language interpretation만 수행합니다. menu_taste_claims와 user_preference_claims를 분리하세요. generic satisfaction/service/delivery는 Taste claim이 아닙니다. Explicit user preference + confidence >= .75만 user learning에 사용합니다. API key가 없을 때 regex fallback으로 가장하지 마세요.

## 5. UI pass — discovery
Attach: `components/TasteLensApp.tsx`, `components/SafeImage.tsx`, `app/globals.css`

Prompt:
> Onboarding → Home → Taste Lens → Food recommendation UI만 개선하세요. API contract와 state transition은 유지하세요. Taste Lens가 기존 배달앱 위의 Food Discovery Layer로 보이게 하세요. Pairwise 10회와 Auto/Category 흐름을 유지하세요.

## 6. UI pass — restaurant/menu
Prompt:
> Food → Restaurant → Restaurant Detail → Menu UI만 개선하세요. Restaurant 대표사진, selected Food Taste Match, rating, review count, delivery time/fee/minimum order, menu image/name/description/price/taste match를 유지하세요. Seller menu order를 Taste score로 재정렬하지 마세요.

## 7. UI pass — learning loop
Prompt:
> Order → optional taste-change explanation → order history → review → optional review-impact explanation → profile을 개선하세요. Learning automatic / Explanation optional 원칙을 유지하세요. Rating은 satisfaction signal이지 Taste Vector direct update가 아닙니다.

## 8. Final consistency
Prompt:
> Product logic과 architecture를 재설계하지 마세요. broken import, missing env, API mismatch, dead-end navigation, responsive UI, image fallback, Supabase Storage URL handling만 점검하세요. 최종 흐름 Taste → Food → Restaurant → Menu → Order → Review → Learning을 보존하세요.
