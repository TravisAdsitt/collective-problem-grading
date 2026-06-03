"""
Tiny stdlib HTTP-GET-JSON helper shared by the fetchers.

Uses urllib so the project needs no third-party dependency. Network calls are
isolated in get_json() so fetchers can be unit-tested by monkeypatching it.
"""
from __future__ import annotations

import json
import logging
import time
import urllib.error
import urllib.parse
import urllib.request

log = logging.getLogger(__name__)

_USER_AGENT = "AccountabilityLedger/1.0 (+https://github.com/; research use)"


def build_url(base: str, params: dict[str, str]) -> str:
    """Join a base URL with a query string, dropping None/empty values."""
    clean = {k: v for k, v in params.items() if v not in (None, "")}
    sep = "&" if "?" in base else "?"
    return f"{base}{sep}{urllib.parse.urlencode(clean)}" if clean else base


def get_json(url: str, *, timeout: float = 30.0, retries: int = 3, backoff: float = 2.0) -> dict | list:
    """GET a URL and parse JSON, retrying on transient errors.

    Raises the last error if all attempts fail. Keep network use confined here.
    """
    last_err: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError) as e:
            last_err = e
            status = getattr(e, "code", None)
            # 4xx other than 429 won't get better by retrying.
            if status and 400 <= status < 500 and status != 429:
                break
            wait = backoff ** (attempt - 1)
            log.warning("GET failed (attempt %d/%d): %s — retrying in %.1fs", attempt, retries, e, wait)
            time.sleep(wait)
    raise RuntimeError(f"GET failed after {retries} attempt(s): {url}") from last_err
