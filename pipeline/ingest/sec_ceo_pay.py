"""
SEC CEO-to-Median-Worker Pay Ratio — required disclosure under Dodd-Frank §953(b).

Source: SEC EDGAR proxy statements (DEF 14A filings), or aggregators:
  - AFL-CIO Executive Paywatch: https://aflcio.org/paywatch
  - Economic Policy Institute: https://epi.org/

File to place: data/raw/sec_ceo_pay/ratios.csv

Expected columns:
  Company, Ticker, CEO Name, CEO Total Compensation (USD),
  Median Worker Pay (USD), Pay Ratio (e.g. "350:1"),
  Fiscal Year (YYYY)

Interpretation: lower ratio = more equitable pay distribution.
S&P 500 median ratio is roughly 200:1; ratios above 500:1 signal extreme inequality.
This is a disclosed fact, not a pledge — high data reliability for covered companies.
"""
from typing import Iterator
from .base import BaseIngester


class SEOCeoPayIngester(BaseIngester):
    source_name = "sec_ceo_pay"

    def ingest(self) -> Iterator[dict]:
        for row in self._csv_rows("ratios.csv"):
            yield {
                "source": "SEC CEO Pay Ratio (DEF 14A)",
                "name": row.get("Company", "").strip(),
                "ticker": row.get("Ticker", "").strip().upper(),
                "ceo_name": row.get("CEO Name", "").strip(),
                "ceo_total_comp": row.get("CEO Total Compensation (USD)", "").strip(),
                "median_worker_pay": row.get("Median Worker Pay (USD)", "").strip(),
                "pay_ratio": row.get("Pay Ratio", "").strip(),
                "as_of": row.get("Fiscal Year", "").strip(),
                "url": "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&type=DEF+14A",
            }
