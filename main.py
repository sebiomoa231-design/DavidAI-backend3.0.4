import importlib
import logging
import sys

# Compatibility shim: allow code that imports modules under the david.* package
# to find existing top-level modules in this repository without reorganizing files.
# This is intentionally defensive: we only map modules that successfully import.
_top_level_modules = [
    # core modules that exist at repo root
    "ai_router",
    "auth",
    "base",
    "cache",
    "calculator",
    "cerebras",
    "david",
    "decisions",
    "gemini",
    "groq",
    "huggingface",
    "json_store",
    "learning",
    "logger",
    "memory_engine",
    "metrics",
    "models",
    "notes",
    "openrouter",
    "owner",
    "permissions",
    "plugin_manager",
    "projects",
    "registry",
    "research",
    "routes_auth",
    "routes_core",
    "routes_capabilities",
    "routes_export",
    "routes_learning",
    "routes_memory",
    "routes_permissions",
    "routes_plugins",
    "routes_projects",
    "routes_providers",
    "routes_research",
    "routes_tasks",
    "routes_uploads",
    "routes_vision",
    "routes_voice",
    "sambanova",
    "settings",
    "start",
    "tasks",
    "tool_manager",
    "vision_engine",
    "workspace",
]

_package_prefixes = [
    "david.core",
    "david.config",
    "david.memory",
    "david.router",
    "david.security",
    "david.planning",
    "david.metrics",
    "david.utils",
]

for mod_name in _top_level_modules:
    try:
        top_mod = importlib.import_module(mod_name)
    except Exception:
        # Not importable at this time (maybe has heavy deps) — skip mapping
        logging.debug(f"Shim: top-level module {mod_name} not importable now; skipping")
        continue
    # Insert a few likely aliases so imports like 'david.memory.memory_engine'
    # resolve to the existing top-level module object
    for prefix in _package_prefixes:
        alias = f"{prefix}.{mod_name}"
        if alias not in sys.modules:
            sys.modules[alias] = top_mod
    # also map 'david.<mod_name>' to the top-level module
    alias_direct = f"david.{mod_name}"
    if alias_direct not in sys.modules:
        sys.modules[alias_direct] = top_mod

from fastapi import FastAPI

app = FastAPI(title="David AI")


@app.get("/api/health")
async def health():
    return {"status": "ok"}


# Try to include routers if they exist. Import errors are caught so the app still starts.
def try_include(router_module_name: str, attr: str = "router"):
    try:
        mod = __import__(router_module_name, fromlist=[attr])
        router = getattr(mod, attr)
        app.include_router(router)
        logging.info(f"Included router {router_module_name}")
    except Exception as e:
        logging.warning(f"Could not include {router_module_name}: {e}")


# Common route modules present in the repo root. We attempt to wire them but won't fail on import errors.
_router_modules = [
    "routes_auth",
    "routes_core",
    "routes_capabilities",
    "routes_export",
    "routes_learning",
    "routes_memory",
    "routes_permissions",
    "routes_plugins",
    "routes_projects",
    "routes_providers",
    "routes_research",
    "routes_tasks",
    "routes_uploads",
    "routes_vision",
    "routes_voice",
]

for _m in _router_modules:
    try_include(_m)


if __name__ == "__main__":
    import uvicorn, os

    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
