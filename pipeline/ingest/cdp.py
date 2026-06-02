"""
CDP (Carbon Disclosure Project) — climate scores.

Download: https://www.cdp.net/en/scores (requires registration for full dataset;
  the A-List is publicly available at https://www.cdp.net/en/companies/companies-scores)
File to place: data/raw/cdp/scores.csv

Expected columns:
  Account Name, Primary Ticker, Country/Region, Industry (Megasector),
  CDP Score (A|A-|B|B-|C|D|F),
  Response Year (YYYY)

CDP scores measure TRANSPARENCY and ENVIRONMENTAL AMBITION in reporting.
An A means full disclosure + leadership action; D means minimal disclosure.
Note: CDP scores correlate with reporting quality, not necessarily real-world outcomes.
Cross-reference with SBTi for target verification and InfluenceMap for lobbying reality.
"""
from typing import Iterator
from .base import BaseIngester


class CDPIngester(BaseIngester):
    source_name = "cdp"

    def ingest(self) -> Iterator[dict]:
        for row in self._csv_rows("scores.csv"):
            yield {
                "source": "CDP",
                "name": row.get("Account Name", "").strip(),
                "ticker": row.get("Primary Ticker", "").strip().upper(),
                "sector": row.get("Industry (Megasector)", "").strip(),
                "score": row.get("CDP Score", "").strip(),
                "as_of": row.get("Response Year", "").strip(),
                "url": "https://www.cdp.net/en/companies/companies-scores",
            }
