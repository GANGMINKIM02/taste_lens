import os
from urllib.parse import quote

BUCKET=os.getenv('SUPABASE_ASSET_BUCKET','taste-lens-assets').strip() or 'taste-lens-assets'

def public_asset_base_url() -> str:
    supabase=os.getenv('SUPABASE_URL','').strip().rstrip('/')
    if supabase:
        return f"{supabase}/storage/v1/object/public/{BUCKET}"
    # Used only by pure seed/unit tests; real persistence still requires Supabase envs.
    return f"https://assets.invalid/{BUCKET}"

def asset_url(path:str)->str:
    return f"{public_asset_base_url()}/{quote(path, safe='/_-')}"
