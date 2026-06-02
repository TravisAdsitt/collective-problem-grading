"""
Access to Medicine Index — getting drugs/vaccines to low- & middle-income countries.

Download: https://accesstomedicine.org/amindex/  (Excel/CSV export on the data page)
File to place: data/raw/access_to_medicine/rankings.csv

Expected columns:
  Rank, Company, Headquartered, Overall Score (0–100),
  R&D Score, Pricing Score, Manufacturing & Supply Score,
  Patents & Licensing Score, Governance Score,
  Edition Year (YYYY)

Scope: pharmaceutical and biotech companies only. Non-pharma entities are unrated here.
2024 finding: Novartis #1, GSK #2; overall momentum STALLED —
  "comprehensive policies" outpacing implementation.
This is a clean example of the pledge_vs_action_gap in health.
"""
from typing import Iterator
from .base import BaseIngester


class AccessToMedicineIngester(BaseIngester):
    source_name = "access_to_medicine"

    def ingest(self) -> Iterator[dict]:
        for row in self._csv_rows("rankings.csv"):
            yield {
                "source": "Access to Medicine Index",
                "name": row.get("Company", "").strip(),
                "rank": row.get("Rank", "").strip(),
                "overall_score": row.get("Overall Score", "").strip(),
                "rd_score": row.get("R&D Score", "").strip(),
                "pricing_score": row.get("Pricing Score", "").strip(),
                "manufacturing_score": row.get("Manufacturing & Supply Score", "").strip(),
                "patents_score": row.get("Patents & Licensing Score", "").strip(),
                "governance_score": row.get("Governance Score", "").strip(),
                "as_of": row.get("Edition Year", "").strip(),
                "url": "https://accesstomedicine.org/amindex/",
            }
