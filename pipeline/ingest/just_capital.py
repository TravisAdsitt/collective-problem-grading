"""
JUST Capital — worker pay, benefits, community, environment, customer, management.

Download: https://justcapital.com/rankings/ (CSV download available)
File to place: data/raw/just_capital/rankings.csv

Expected columns:
  Rank, Company, Ticker, Industry,
  Overall Score (0–100), Workers Score, Communities Score,
  Environment Score, Customers Score, Shareholders Score,
  Ranking Year (YYYY)

Scope: large U.S. public companies; good S&P 500 coverage.
Weights are survey-derived from American public opinion — a feature and a limitation.
"""
from typing import Iterator
from .base import BaseIngester


class JUSTCapitalIngester(BaseIngester):
    source_name = "just_capital"

    def ingest(self) -> Iterator[dict]:
        for row in self._csv_rows("rankings.csv"):
            yield {
                "source": "JUST Capital",
                "name": row.get("Company", "").strip(),
                "ticker": row.get("Ticker", "").strip().upper(),
                "rank": row.get("Rank", "").strip(),
                "industry": row.get("Industry", "").strip(),
                "overall_score": row.get("Overall Score", "").strip(),
                "workers_score": row.get("Workers Score", "").strip(),
                "communities_score": row.get("Communities Score", "").strip(),
                "environment_score": row.get("Environment Score", "").strip(),
                "as_of": row.get("Ranking Year", "").strip(),
                "url": "https://justcapital.com/rankings/",
            }
