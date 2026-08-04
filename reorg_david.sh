#!/usr/bin/env bash
set -euo pipefail

# Reorganize repository into david package layout (git-history preserving moves)
# Usage: run this from repository root on a new branch.
# It will create branch reorg/david-package, move files with git mv,
# create package __init__ files and a conservative import-updater script.
# Review changes and .bak files before committing/pushing.

BRANCH="reorg/david-package"

echo "Creating branch $BRANCH"
git fetch origin
git checkout -b "$BRANCH"

# create package directories
mkdir -p david/{core,router,memory,planning,config,security,utils,providers,routes}

# create minimal __init__ files so packages exist
echo "# david package" > david/__init__.py
for sub in core router memory planning config security utils providers routes; do
  echo "# $sub package" > "david/$sub/__init__.py"
done

# helper to move if exists
mv_if_exists() {
  src="$1"
  dst="$2"
  if [ -f "$src" ]; then
    git mv "$src" "$dst"
    echo "Moved $src -> $dst"
  else
    echo "Skipped missing: $src"
  fi
}

# core
mv_if_exists "david.py" "david/core/david.py"
mv_if_exists "owner.py" "david/core/owner.py"
mv_if_exists "decisions.py" "david/core/decisions.py"
mv_if_exists "base.py" "david/core/base.py"
mv_if_exists "calculator.py" "david/core/calculator.py"
mv_if_exists "notes.py" "david/core/notes.py"

# config
mv_if_exists "settings.py" "david/config/settings.py"
mv_if_exists "pyproject.toml.txt" "david/config/pyproject.toml.txt"

# memory
mv_if_exists "memory_engine.py" "david/memory/memory_engine.py"
mv_if_exists "json_store.py" "david/memory/json_store.py"
mv_if_exists "cache.py" "david/memory/cache.py"

# planning
mv_if_exists "projects.py" "david/planning/projects.py"
mv_if_exists "tasks.py" "david/planning/tasks.py"
mv_if_exists "registry.py" "david/planning/registry.py"

# security
mv_if_exists "auth.py" "david/security/auth.py"
mv_if_exists "permissions.py" "david/security/permissions.py"
mv_if_exists "workspace.py" "david/security/workspace.py"

# utils
mv_if_exists "logger.py" "david/utils/logger.py"
mv_if_exists "metrics.py" "david/utils/metrics.py"
mv_if_exists "models.py" "david/utils/models.py"
mv_if_exists "learning.py" "david/utils/learning.py"
mv_if_exists "plugin_manager.py" "david/utils/plugin_manager.py"
mv_if_exists "tool_manager.py" "david/utils/tool_manager.py"

# providers
mv_if_exists "huggingface.py" "david/providers/huggingface.py"
mv_if_exists "openrouter.py" "david/providers/openrouter.py"
mv_if_exists "gemini.py" "david/providers/gemini.py"
mv_if_exists "groq.py" "david/providers/groq.py"
mv_if_exists "sambanova.py" "david/providers/sambanova.py"
mv_if_exists "cerebras.py" "david/providers/cerebras.py"
mv_if_exists "vision_engine.py" "david/providers/vision_engine.py"

# routes -> david.routes
mv_if_exists "routes_core.py" "david/routes/routes_core.py"
mv_if_exists "routes_auth.py" "david/routes/routes_auth.py"
mv_if_exists "routes_capabilities.py" "david/routes/routes_capabilities.py"
mv_if_exists "routes_export.py" "david/routes/routes_export.py"
mv_if_exists "routes_learning.py" "david/routes/routes_learning.py"
mv_if_exists "routes_memory.py" "david/routes/routes_memory.py"
mv_if_exists "routes_permissions.py" "david/routes/routes_permissions.py"
mv_if_exists "routes_plugins.py" "david/routes/routes_plugins.py"
mv_if_exists "routes_projects.py" "david/routes/routes_projects.py"
mv_if_exists "routes_providers.py" "david/routes/routes_providers.py"
mv_if_exists "routes_research.py" "david/routes/routes_research.py"
mv_if_exists "routes_tasks.py" "david/routes/routes_tasks.py"
mv_if_exists "routes_uploads.py" "david/routes/routes_uploads.py"
mv_if_exists "routes_vision.py" "david/routes/routes_vision.py"
mv_if_exists "routes_voice.py" "david/routes/routes_voice.py"

# create import updater
cat > update_imports.py <<'PY'
#!/usr/bin/env python3
# AST-based import updater. Creates .bak backups for changed files.
import ast, astor, os

MAPPING = {
    "ai_router": "david.router.ai_router",
    "auth": "david.security.auth",
    "settings": "david.config.settings",
    "memory_engine": "david.memory.memory_engine",
    "json_store": "david.memory.json_store",
    "owner": "david.core.owner",
    "david": "david.core.david",
    "projects": "david.planning.projects",
    "tasks": "david.planning.tasks",
    "registry": "david.planning.registry",
    "logger": "david.utils.logger",
    "metrics": "david.utils.metrics",
    "models": "david.utils.models",
    "plugin_manager": "david.utils.plugin_manager",
    "tool_manager": "david.utils.tool_manager",
    "huggingface": "david.providers.huggingface",
    "openrouter": "david.providers.openrouter",
    "gemini": "david.providers.gemini",
    "groq": "david.providers.groq",
    "sambanova": "david.providers.sambanova",
    "cerebras": "david.providers.cerebras",
    "vision_engine": "david.providers.vision_engine",
    "cache": "david.memory.cache",
    "routes_core": "david.routes.routes_core",
    "routes_auth": "david.routes.routes_auth",
}


def rewrite(path):
    with open(path, "r", encoding="utf-8") as f:
        src = f.read()
    try:
        tree = ast.parse(src)
    except Exception as e:
        print("SKIP parse error:", path, e)
        return False
    nonlocal_changed = [False]
    class T(ast.NodeTransformer):
        def visit_Import(self, node):
            for alias in node.names:
                if alias.name in MAPPING:
                    alias.name = MAPPING[alias.name]
                    nonlocal_changed[0] = True
            return node
        def visit_ImportFrom(self, node):
            if node.module and node.module in MAPPING:
                node.module = MAPPING[node.module]
                nonlocal_changed[0] = True
            return node
    T().visit(tree)
    if nonlocal_changed[0]:
        with open(path + ".bak", "w", encoding="utf-8") as f:
            f.write(src)
        new = astor.to_source(tree)
        with open(path, "w", encoding="utf-8") as f:
            f.write(new)
        print("UPDATED", path)
        return True
    return False

for root, _, files in os.walk("."):
    if any(part in (".git", "david", ".venv", "venv", "__pycache__") for part in root.split(os.sep)):
        continue
    for fn in files:
        if fn.endswith(".py"):
            rewrite(os.path.join(root, fn))

print("Done. Review .bak files for changes.")
PY

chmod +x update_imports.py

# run updater
python3 update_imports.py || true

# Patch main.py router names
python3 - <<'PY'
from pathlib import Path
p = Path("main.py")
s = p.read_text()
s = s.replace('"routes_auth"', '"david.routes.routes_auth"')
s = s.replace('"routes_core"', '"david.routes.routes_core"')
s = s.replace('"routes_capabilities"', '"david.routes.routes_capabilities"')
s = s.replace('"routes_export"', '"david.routes.routes_export"')
s = s.replace('"routes_learning"', '"david.routes.routes_learning"')
s = s.replace('"routes_memory"', '"david.routes.routes_memory"')
s = s.replace('"routes_permissions"', '"david.routes.routes_permissions"')
s = s.replace('"routes_plugins"', '"david.routes.routes_plugins"')
s = s.replace('"routes_projects"', '"david.routes.routes_projects"')
s = s.replace('"routes_providers"', '"david.routes.routes_providers"')
s = s.replace('"routes_research"', '"david.routes.routes_research"')
s = s.replace('"routes_tasks"', '"david.routes.routes_tasks"')
s = s.replace('"routes_uploads"', '"david.routes.routes_uploads"')
s = s.replace('"routes_vision"', '"david.routes.routes_vision"')
s = s.replace('"routes_voice"', '"david.routes.routes_voice"')
p.write_text(s)
print('Patched main.py router names (review manually).')
PY

# show status
git status --porcelain

echo "Reorg script finished. Inspect changes, then run to commit/push:" 
echo "  git add -A" 
echo "  git commit -m 'Reorganize repo into david package'" 
echo "  git push -u origin $BRANCH"
