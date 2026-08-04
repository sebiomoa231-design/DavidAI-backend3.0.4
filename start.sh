#!/usr/bin/env bash
set -euo pipefail

# Default start for FastAPI apps: uses uvicorn and the $PORT env var Render sets
if [ $# -eq 0 ]; then
  exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --workers ${WEB_CONCURRENCY:-1}
else
  exec "$@"
fi
