import os
from functools import lru_cache
from typing import Any
from dotenv import load_dotenv

load_dotenv()

@lru_cache
def get_db() -> Any:
    url=os.getenv('SUPABASE_URL','').strip()
    key=os.getenv('SUPABASE_SECRET_KEY','').strip()
    if not url or not key:
        raise RuntimeError('SUPABASE_URL and SUPABASE_SECRET_KEY are required')
    try:
        from supabase import create_client
    except Exception as exc:
        raise RuntimeError('Supabase Python client is not installed correctly. Run: pip install -r requirements.txt') from exc
    return create_client(url,key)

def configured() -> bool:
    return bool(os.getenv('SUPABASE_URL','').strip() and os.getenv('SUPABASE_SECRET_KEY','').strip())
