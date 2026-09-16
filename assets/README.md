# Taste Lens image assets — PRD v4.3

Runtime image generation is intentionally **not** part of the app. The PRD image architecture is implemented as:

`offline image generator (FLUX / Ideogram / other) → WebP optimization → Supabase Storage → database URL → Next.js Image`

1. `python scripts/build_image_manifest.py`
2. Generate each row in `assets/image_manifest.csv` using the image tool of your choice. Save source files under `assets/generated/<target_path>` (PNG/JPG/WebP accepted).
3. `python scripts/optimize_images.py`
4. Configure root `.env` with Supabase credentials.
5. `python scripts/upload_assets.py`
6. `python -m backend.app.seed_supabase`
7. `python scripts/validate_assets.py`

The manifest contains exactly **70 Food + 41 Restaurant + 120 Menu = 231 unique production images**. Food and Restaurant images are always unique. The menu pool is deliberately reused according to the PRD, but never repeats within one restaurant detail screen; Korean foods receive at least four variants for comparison/demo paths.

For a contest demo, the app also ships three tiny local fallback files under `public/fallback/`. They are failure-only placeholders, not production assets.
