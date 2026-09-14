"""Optional Render keep-alive worker.

This runs in the backend process only when KEEP_ALIVE_ENABLED is enabled.
It is intentionally configurable because external monitoring or a paid
always-on instance is the more reliable production solution.
"""
import logging
import os
import threading
import urllib.request

logger = logging.getLogger(__name__)


def _enabled(value: str | None) -> bool:
    return (value or "false").lower() in {"1", "true", "yes", "on"}


def start_keep_alive() -> threading.Event | None:
    if not _enabled(os.getenv("KEEP_ALIVE_ENABLED")):
        return None

    url = os.getenv("KEEP_ALIVE_URL", "https://www.kalyanienterprises.com/health")
    try:
        interval_minutes = max(1, int(os.getenv("KEEP_ALIVE_INTERVAL_MINUTES", "5")))
    except ValueError:
        interval_minutes = 5

    stop_event = threading.Event()

    def worker() -> None:
        while not stop_event.is_set():
            try:
                with urllib.request.urlopen(url, timeout=10) as response:
                    response.read(1)
                logger.info("Keep-alive request succeeded: %s", url)
            except Exception as error:  # Keep the app running if the endpoint is unavailable.
                logger.warning("Keep-alive request failed: %s", error)

            stop_event.wait(interval_minutes * 60)

    thread = threading.Thread(target=worker, daemon=True, name="keep-alive-pinger")
    thread.start()
    logger.info("Keep-alive enabled: %s every %s minute(s)", url, interval_minutes)
    return stop_event
