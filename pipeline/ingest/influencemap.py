"""
InfluenceMap — climate lobbying alignment scores.

Download: https://influencemap.org/scores
File to place: data/raw/influencemap/company_scores.csv

Expected columns (as exported from InfluenceMap):
  Company Name, Ticker, Country, Sector,
  Band (A+|A|B+|B|C+|C|C-|D+|D|E|F),
  Performance Score (-100 to 100),
  Influence Score,
  As Of (YYYY-MM)

InfluenceMap measures political/lobbying ALIGNMENT with climate science.
High scores (A+/A) = lobbying for ambitious climate policy.
Low scores (D/E/F) = obstructing or delaying climate policy.

Crucially: ~80% of the 25 most climate-obstructive companies had net-zero pledges.
This is the canonical source for pledge_vs_action_gap on climate.
"""
from typing import Iterator
from .base import BaseIngester


class InfluenceMapIngester(BaseIngester):
    source_name = "influencemap"

    def ingest(self) -> Iterator[dict]:
        for row in self._csv_rows("company_scores.csv"):
            yield {
                "source": "InfluenceMap",
                "name": row.get("Company Name", "").strip(),
                "ticker": row.get("Ticker", "").strip().upper(),
                "sector": row.get("Sector", "").strip(),
                "band": row.get("Band", "").strip(),
                "performance_score": row.get("Performance Score", "").strip(),
                "influence_score": row.get("Influence Score", "").strip(),
                "as_of": row.get("As Of", "").strip(),
                "url": f"https://influencemap.org/company/{row.get('Company Name', '').replace(' ', '-')}",
            }
