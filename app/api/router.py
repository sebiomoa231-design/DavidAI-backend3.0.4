"""
Bridge for import path 'app.api.router' -> uses top-level router.py which
already defines `api_router`. This shim imports the repo-root router module
and re-exports api_router for main.py, etc.
"""
from importlib import import_module

try:
    _root_router = import_module("router")  # expects router.py at repo root
    api_router = getattr(_root_router, "api_router")
except Exception:  # defensive fallback to avoid import-time failure
    from fastapi import APIRouter
    api_router = APIRouter()
