"""
ProPublica IRS Files — tax conduct for individuals and foundations.

Source: ProPublica's "IRS Files" investigation and Nonprofit Explorer.
  https://projects.propublica.org/nonprofits/
  https://www.propublica.org/series/the-irs-files

File to place: data/raw/propublica_irs/individuals.csv

Expected columns:
  Name, Net Worth Estimate (USD), Estimated Income (USD),
  Estimated Federal Tax Rate (%), Statutory Top Rate (%),
  Tax Rate Gap (pp — difference from statutory),
  Foundation Payout Rate (%), Foundation Name,
  Source Notes, Year (YYYY)

Documented facts only; reader draws conclusions.
"""
from typing import Iterator
from .base import BaseIngester


class ProPublicaIRSIngester(BaseIngester):
    source_name = "propublica_irs"

    def ingest(self) -> Iterator[dict]:
        for row in self._csv_rows("individuals.csv"):
            yield {
                "source": "ProPublica IRS Files",
                "name": row.get("Name", "").strip(),
                "entity_type": "individual",
                "net_worth_usd": row.get("Net Worth Estimate (USD)", "").strip(),
                "estimated_income_usd": row.get("Estimated Income (USD)", "").strip(),
                "effective_tax_rate_pct": row.get("Estimated Federal Tax Rate (%)", "").strip(),
                "statutory_rate_pct": row.get("Statutory Top Rate (%)", "").strip(),
                "tax_rate_gap_pp": row.get("Tax Rate Gap (pp)", "").strip(),
                "foundation_payout_rate_pct": row.get("Foundation Payout Rate (%)", "").strip(),
                "foundation_name": row.get("Foundation Name", "").strip(),
                "source_notes": row.get("Source Notes", "").strip(),
                "as_of": row.get("Year", "").strip(),
                "url": "https://projects.propublica.org/tax-cuts-and-jobs-act/",
            }
