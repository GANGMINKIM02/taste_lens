"""Vercel Python entrypoint.

The core FastAPI application lives in backend.app.main and is mounted under /api
so the Next.js frontend and Python API deploy on the same Vercel domain.
"""
from fastapi import FastAPI
from backend.app.main import app as core_app

app = FastAPI(title="Taste Lens Vercel Gateway", docs_url=None, redoc_url=None)
app.mount("/api", core_app)
