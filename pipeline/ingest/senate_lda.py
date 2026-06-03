"""
Senate LDA — federal lobbying spend (replaces the discontinued OpenSecrets API).

Populate via: python3 -m pipeline.fetch.senate_lda --year 2024
File read:    data/raw/senate_lda/lobbying.csv

Expected columns (written by the fetcher):
  Client, Ticker, Total Lobbying Spend (USD), Filings, Year

Lobbying spend is documented ACTION (money spent influencing federal policy),
not a pledge — it feeds the tax_governance domain as evidence.
"""
from typing import Iterator
from .base import BaseIngester


class SenateLDAIngester(BaseIngester):
    source_name = "senate_lda"

    def ingest(self) -> Iterator[dict]:
        for row in self._csv_rows("lobbying.csv"):
            yield {
                "source": "U.S. Senate (Lobbying Disclosure Act)",
                "data_type": "lobbying",
                "name": row.get("Client", "").strip(),
                "ticker": row.get("Ticker", "").strip().upper(),
                "total_lobbying_usd": row.get("Total Lobbying Spend (USD)", "").strip(),
                "filings": row.get("Filings", "").strip(),
                "as_of": row.get("Year", "").strip(),
                "url": "https://lda.senate.gov/filings/public/filing/search/",
            }
