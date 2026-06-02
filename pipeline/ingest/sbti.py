"""
Science Based Targets initiative (SBTi) — verified emissions targets.

Download: https://sciencebasedtargets.org/companies-taking-action
File to place: data/raw/sbti/targets.csv

Expected columns:
  Company Name, ISIN, Ticker, Country, Sector,
  Status (Committed|Targets Set|Approved|Achieved|Removed|No longer valid),
  Target Year, Scope, Near-Term Target, Long-Term Target,
  Date Published (YYYY-MM-DD)

SBTi is the gold standard for verified science-aligned emissions targets.
"Committed" = signed letter of intent only (low-confidence pledge).
"Targets Set" = submitted but not yet validated.
"Approved" = independently validated against 1.5°C pathway — this is the action signal.
"Achieved" = target met.
Cross-reference with InfluenceMap: an SBTi-approved company lobbying against climate
policy is a severe pledge_vs_action_gap.
"""
from typing import Iterator
from .base import BaseIngester


class SBTiIngester(BaseIngester):
    source_name = "sbti"

    def ingest(self) -> Iterator[dict]:
        for row in self._csv_rows("targets.csv"):
            yield {
                "source": "SBTi",
                "name": row.get("Company Name", "").strip(),
                "ticker": row.get("Ticker", "").strip().upper(),
                "isin": row.get("ISIN", "").strip(),
                "sector": row.get("Sector", "").strip(),
                "status": row.get("Status", "").strip(),
                "target_year": row.get("Target Year", "").strip(),
                "near_term_target": row.get("Near-Term Target", "").strip(),
                "long_term_target": row.get("Long-Term Target", "").strip(),
                "as_of": row.get("Date Published", "").strip()[:7],
                "url": "https://sciencebasedtargets.org/companies-taking-action",
            }
