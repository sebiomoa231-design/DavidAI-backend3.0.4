"""Compatibility package shim for `david`.

This file makes it possible for existing code that imports `david.*` to
keep working without moving files around. It dynamically loads the
original top-level modules from the repository root and exposes them
under the `david` package namespace and appropriate subpackages.

This is conservative and non-destructive — it doesn't delete or move
any existing files. It just creates in-memory module aliases under the
`david.*` names so imports like `from david.config.settings import ...`
continue to work.

If you later want to perform a full repo refactor (moving files into a
real package on disk), this shim can be removed.
"""

from importlib.machinery import SourceFileLoader
import importlib.util
import importlib
import sys
import os
import types

pkg_dir = os.path.dirname(__file__)
repo_root = os.path.abspath(os.path.join(pkg_dir, ".."))

# Mapping: target module name under david.* -> source file at repo root
MODULE_MAP = {
    "david.core.david": "david.py",
    "david.config.settings": "settings.py",
    "david.router.ai_router": "ai_router.py",
    "david.router.cache": "cache.py",
    "david.router.metrics": "metrics.py",
    "david.router.ai_router": "ai_router.py",
    "david.memory.memory_engine": "memory_engine.py",
    "david.memory.json_store": "json_store.py",
    "david.core.owner": "owner.py",
    "david.core.decisions": "decisions.py",
    "david.core.base": "base.py",
    "david.core.calculator": "calculator.py",
    "david.core.notes": "notes.py",
    "david.providers.huggingface": "huggingface.py",
    "david.providers.openrouter": "openrouter.py",
    "david.providers.gemini": "gemini.py",
    "david.providers.groq": "groq.py",
    "david.providers.cerebras": "cerebras.py",
    "david.providers.sambanova": "sambanova.py",
    "david.providers.vision_engine": "vision_engine.py",
    "david.utils.logger": "logger.py",
    "david.utils.models": "models.py",
    "david.utils.learning": "learning.py",
    "david.utils.plugin_manager": "plugin_manager.py",
    "david.utils.tool_manager": "tool_manager.py",
    "david.planning.projects": "projects.py",
    "david.planning.tasks": "tasks.py",
    "david.planning.registry": "registry.py",
    "david.security.auth": "auth.py",
    "david.security.permissions": "permissions.py",
    "david.security.workspace": "workspace.py",
    "david.routes.routes_core": "routes_core.py",
    "david.routes.routes_auth": "routes_auth.py",
    "david.routes.routes_capabilities": "routes_capabilities.py",
    "david.routes.routes_export": "routes_export.py",
    "david.routes.routes_learning": "routes_learning.py",
    "david.routes.routes_memory": "routes_memory.py",
    "david.routes.routes_permissions": "routes_permissions.py",
    "david.routes.routes_plugins": "routes_plugins.py",
    "david.routes.routes_projects": "routes_projects.py",
    "david.routes.routes_providers": "routes_providers.py",
    "david.routes.routes_research": "routes_research.py",
    "david.routes.routes_tasks": "routes_tasks.py",
    "david.routes.routes_uploads": "routes_uploads.py",
    "david.routes.routes_vision": "routes_vision.py",
    "david.routes.routes_voice": "routes_voice.py",
}


def _ensure_parent_module(parent_name: str):
    """Ensure that a parent package exists in sys.modules and as an attribute
    on this package. E.g., for parent_name 'david.router' create a module
    object so that imports like 'from david.router import ai_router' work."""
    if parent_name in sys.modules:
        return sys.modules[parent_name]
    mod = types.ModuleType(parent_name)
    mod.__path__ = [os.path.join(repo_root, "david", *(parent_name.split(".")[1:]))]
    sys.modules[parent_name] = mod
    # also set attribute on top-level david package so attribute access works
    top = sys.modules.get(__name__)
    if top is not None:
        parts = parent_name.split(".")
        if len(parts) == 2:
            setattr(top, parts[1], mod)
    return mod


for target_mod, src_file in MODULE_MAP.items():
    try:
        abs_path = os.path.join(repo_root, src_file)
        if not os.path.exists(abs_path):
            # file doesn't exist in repo root; skip
            continue

        # Ensure parent packages exist (david, david.core, etc.)
        parts = target_mod.split('.')
        for i in range(1, len(parts)):
            parent = '.'.join(parts[:i+1]) if i > 0 else parts[0]
            if parent == __name__:
                continue
            _ensure_parent_module(parent)

        # Load the source file as module with the desired target_mod name
        if target_mod in sys.modules:
            continue

        loader = SourceFileLoader(target_mod, abs_path)
        spec = importlib.util.spec_from_loader(loader.name, loader)
        module = importlib.util.module_from_spec(spec)
        loader.exec_module(module)
        sys.modules[target_mod] = module

        # Attach module to its parent package as attribute for attribute access
        parent_name = '.'.join(parts[:-1])
        parent_mod = sys.modules.get(parent_name)
        if parent_mod is not None:
            setattr(parent_mod, parts[-1], module)

    except Exception as e:
        # tolerate errors during the shim installation; runtime imports may still
        # work via other fallbacks (main.py includes its own shim as well).
        # We keep this quiet to avoid noisy startup logs.
        logging = importlib.import_module('logging')
        logging.debug(f"david shim: failed to load {src_file} -> {target_mod}: {e}")

# Expose a small helper for debugging
__all__ = [name.split('.')[-1] for name in MODULE_MAP.keys()]
