"""
Expose logging helpers expected by app.core.* imports. Prefer the repository's
app_logging.py but provide a small fallback logger if it fails to import.
"""
from importlib import import_module

try:
    _mod = import_module("app_logging")
    logger = getattr(_mod, "logger")
    log_startup = getattr(_mod, "log_startup")
    log_shutdown = getattr(_mod, "log_shutdown")
    log_request = getattr(_mod, "log_request")
    log_error = getattr(_mod, "log_error")
    log_provider_selection = getattr(_mod, "log_provider_selection")
    log_upload = getattr(_mod, "log_upload")
except Exception:
    import logging
    logger = logging.getLogger("david_ai_fallback")
    logging.basicConfig(level=logging.INFO)

    def log_startup() -> None:
        logger.info("Starting (fallback)")

    def log_shutdown() -> None:
        logger.info("Shutting down (fallback)")

    def log_request(method: str, path: str) -> None:
        logger.info(f"Request: {method} {path}")

    def log_error(context: str, error: Exception) -> None:
        logger.error(f"Error in {context}: {error}")

    def log_provider_selection(provider: str) -> None:
        logger.info(f"Provider selected: {provider}")

    def log_upload(filename: str, size_bytes: int) -> None:
        logger.info(f"File uploaded: {filename} ({size_bytes} bytes)")
