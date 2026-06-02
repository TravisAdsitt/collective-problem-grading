"""
Entity matching across sources.

Primary key: ticker (for companies). Secondary key: normalized name.
This avoids fuzzy matching where possible since ticker symbols are stable.
"""
from __future__ import annotations
import re


def normalize_name(name: str) -> str:
    """Strip legal suffixes and punctuation for fallback name matching."""
    name = name.lower().strip()
    name = re.sub(r"\b(inc|corp|co|llc|ltd|plc|lp|nv|sa|ag|se|group|holdings?|international)\b\.?", "", name)
    name = re.sub(r"[^a-z0-9 ]", "", name)
    return re.sub(r"\s+", " ", name).strip()


class SourceIndex:
    """Indexes a list of source records by ticker + normalized name for fast lookup."""

    def __init__(self, records: list[dict], ticker_field: str = "ticker", name_field: str = "name"):
        self._by_ticker: dict[str, dict] = {}
        self._by_name: dict[str, dict] = {}
        for r in records:
            t = r.get(ticker_field, "").upper().strip()
            n = normalize_name(r.get(name_field, ""))
            if t:
                self._by_ticker[t] = r
            if n:
                self._by_name[n] = r

    def lookup(self, ticker: str, name: str) -> dict | None:
        t = ticker.upper().strip()
        if t and t in self._by_ticker:
            return self._by_ticker[t]
        n = normalize_name(name)
        return self._by_name.get(n)
