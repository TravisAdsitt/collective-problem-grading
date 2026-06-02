"""
Tax Justice Network / Corporate Tax Haven Index — corporate tax avoidance.

Download:
  - Corporate Tax Haven Index: https://www.taxjustice.net/topics/corporate-tax/corporate-tax-haven-index/
  - FTSE350 / Fortune 500 tax data: https://www.taxjustice.net/
File to place: data/raw/tax_justice/corporate_scores.csv

Expected columns:
  Company, Ticker, Country of Incorporation, Effective Tax Rate (%),
  Statutory Rate Comparison (%), Offshore Subsidiaries Count,
  Haven Score (0–100, higher = more avoidance), Year (YYYY)

Data confidence: medium — effective rates derived from financial filings;
haven scores involve methodology judgment calls.
"""
from typing import Iterator
from .base import BaseIngester


class TaxJusticeIngester(BaseIngester):
    source_name = "tax_justice"

    def ingest(self) -> Iterator[dict]:
        for row in self._csv_rows("corporate_scores.csv"):
            yield {
                "source": "Tax Justice Network",
                "name": row.get("Company", "").strip(),
                "ticker": row.get("Ticker", "").strip().upper(),
                "country": row.get("Country of Incorporation", "").strip(),
                "effective_tax_rate_pct": row.get("Effective Tax Rate (%)", "").strip(),
                "statutory_rate_pct": row.get("Statutory Rate Comparison (%)", "").strip(),
                "offshore_subsidiaries": row.get("Offshore Subsidiaries Count", "").strip(),
                "haven_score": row.get("Haven Score (0–100)", "").strip(),
                "as_of": row.get("Year", "").strip(),
                "url": "https://www.taxjustice.net/topics/corporate-tax/corporate-tax-haven-index/",
            }
