"""
Expose get_settings() under app.core.config by delegating to the existing
repository settings providers at the repository root (config.py or settings.py).
"""
from importlib import import_module

def _find_get_settings():
    candidates = ("config", "settings")
    for name in candidates:
        try:
            mod = import_module(name)
            if hasattr(mod, "get_settings"):
                return getattr(mod, "get_settings")
        except Exception:
            continue
    raise RuntimeError("No settings provider found at repository root (expected config.py or settings.py)")

get_settings = _find_get_settings()
