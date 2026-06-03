"""
Entity matching across sources.

Primary key: ticker (for companies). Secondary key: normalized name.
This avoids fuzzy matching where possible since ticker symbols are stable.
"""
from __future__ import annotations
import re


_LEGAL_SUFFIXES = (
    r"inc|incorporated|corp|corporation|co|company|llc|ltd|limited|plc|lp|llp"
    r"|nv|sa|ag|se|group|holdings?|international"
)


def normalize_name(name: str) -> str:
    """Strip legal suffixes and punctuation for name matching.

    Punctuation is removed first so 'U.S.A.' -> 'usa' and 'Corp.' -> 'corp'
    before suffix stripping runs.
    """
    name = name.lower().strip()
    name = re.sub(r"[^a-z0-9 ]", " ", name)
    name = re.sub(rf"\b({_LEGAL_SUFFIXES})\b", " ", name)
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

    def lookup(self, ticker: str, name: str, aliases: list[str] | None = None) -> dict | None:
        """Resolve a record by ticker, then by normalized name, then by any alias.

        Aliases bridge cross-source naming gaps that normalization can't (e.g.
        "Alphabet" in the entity list vs. "Google DeepMind" in the FLI index).
        """
        t = ticker.upper().strip()
        if t and t in self._by_ticker:
            return self._by_ticker[t]
        for candidate in [name, *(aliases or [])]:
            n = normalize_name(candidate)
            if n and n in self._by_name:
                return self._by_name[n]
        return None
