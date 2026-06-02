"""
Ranking Digital Rights (RDR) — platform/telecom privacy & free-expression practices.

Download: https://rankingdigitalrights.org/index/
File to place: data/raw/ranking_digital_rights/scores.csv

Expected columns:
  Company, Ticker, Type (Platform|Telco),
  Overall Score (0–100), Governance Score, Freedom of Expression Score,
  Privacy Score, Edition Year (YYYY)

Scope: major internet platforms and telecommunications companies.
Measures POLICIES and DISCLOSED PRACTICES, not necessarily verified outcomes.
Data confidence: medium (policy-based, not outcome-verified).
"""
from typing import Iterator
from .base import BaseIngester


class RankingDigitalRightsIngester(BaseIngester):
    source_name = "ranking_digital_rights"

    def ingest(self) -> Iterator[dict]:
        for row in self._csv_rows("scores.csv"):
            yield {
                "source": "Ranking Digital Rights",
                "name": row.get("Company", "").strip(),
                "ticker": row.get("Ticker", "").strip().upper(),
                "company_type": row.get("Type", "").strip(),
                "overall_score": row.get("Overall Score", "").strip(),
                "governance_score": row.get("Governance Score", "").strip(),
                "free_expression_score": row.get("Freedom of Expression Score", "").strip(),
                "privacy_score": row.get("Privacy Score", "").strip(),
                "as_of": row.get("Edition Year", "").strip(),
                "url": "https://rankingdigitalrights.org/index/",
            }
