"""
OpenSecrets / FEC — lobbying spend and political contributions.

Download: https://www.opensecrets.org/bulk-data (requires free API key or bulk download)
File to place: data/raw/opensecrets/lobbying.csv and data/raw/opensecrets/contributions.csv

lobbying.csv expected columns:
  Client (company name), Ticker, Total Lobbying Spend (USD),
  Climate-Related Lobbying (USD, if available), Year (YYYY)

contributions.csv expected columns:
  Donor Organization, Ticker, Total PAC Contributions (USD),
  Cycle (YYYY)

For individuals, use individual-level data from FEC:
  Contributor Name, Employer, Amount (USD), Recipient, Recipient Party,
  Cycle (YYYY)

This is documented fact; reader draws conclusions about direction of spending.
"""
from typing import Iterator
from .base import BaseIngester


class OpenSecretsIngester(BaseIngester):
    source_name = "opensecrets"

    def ingest(self) -> Iterator[dict]:
        for row in self._csv_rows("lobbying.csv"):
            yield {
                "source": "OpenSecrets / FEC",
                "data_type": "lobbying",
                "name": row.get("Client", "").strip(),
                "ticker": row.get("Ticker", "").strip().upper(),
                "total_lobbying_usd": row.get("Total Lobbying Spend (USD)", "").strip(),
                "as_of": row.get("Year", "").strip(),
                "url": "https://www.opensecrets.org/federal-lobbying",
            }
        for row in self._csv_rows("contributions.csv"):
            yield {
                "source": "OpenSecrets / FEC",
                "data_type": "pac_contributions",
                "name": row.get("Donor Organization", "").strip(),
                "ticker": row.get("Ticker", "").strip().upper(),
                "total_pac_usd": row.get("Total PAC Contributions (USD)", "").strip(),
                "as_of": row.get("Cycle", "").strip(),
                "url": "https://www.opensecrets.org/pacs",
            }
