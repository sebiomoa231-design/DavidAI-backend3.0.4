from fastapi import FastAPI
import logging

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
