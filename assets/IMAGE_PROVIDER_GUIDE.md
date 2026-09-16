# Image generator handoff

Taste Lens does **not** generate images during app use.

Recommended offline split:
- Food / RestaurantMenu: FLUX-family image generator (photorealistic food consistency)
- Restaurant representative images: FLUX or Ideogram
- If another image model is available in Timely/your workflow, it is acceptable as long as `assets/image_manifest.csv` target paths are preserved.

Workflow:
1. Feed each manifest prompt to the chosen image generator.
2. Download the generated image immediately to `assets/generated/<target_path>`.
3. Run `python scripts/optimize_images.py`.
4. Run `python scripts/upload_assets.py`.
5. Seed DB with `python -m backend.app.seed_supabase`.

Do not put a FLUX/Ideogram API call in the Next.js/FastAPI user request path. These tools are build-time asset producers only.
