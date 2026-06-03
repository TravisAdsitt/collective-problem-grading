"""
Senate LDA (Lobbying Disclosure Act) fetcher — federal lobbying spend by company.

Replaces the discontinued OpenSecrets API (shut down 2025-04-15). The Senate
LDA database is the *primary* source OpenSecrets itself aggregated, so this is
strictly more authoritative for an actions-over-pledges ledger.

Run LOCALLY (needs network):
    python3 -m pipeline.fetch.senate_lda --year 2024

Writes: data/raw/senate_lda/lobbying.csv
  columns: Client, Ticker, Total Lobbying Spend (USD), Filings, Year
read by pipeline/ingest/senate_lda.py.

API: https://lda.senate.gov/api/  (no key required; register for a key to raise
rate limits, then set LDA_API_KEY). Docs: https://lda.senate.gov/api/redoc/

How spend is attributed to a company:
  Each quarterly filing reports EITHER `income` (a lobbying firm's fee for that
  client) OR `expenses` (a company lobbying in-house). A company's annual spend
  is the sum of both across all of its filings for the year. The LDA client-name
  search is fuzzy, so results are filtered to filings whose client name (or a
  configured alias) normalizes to the target entity — this drops false hits like
  "US APPLE ASSOCIATION" when searching "Apple".
"""
from __future__ import annotations

import argparse
import csv
import logging
import os
import sys
import time
from pathlib import Path

from pipeline.assemble.matcher import normalize_name
from pipeline.fetch.http import build_url, get_json

log = logging.getLogger(__name__)

API_BASE = "https://lda.senate.gov/api/v1/filings/"


def _auth_headers() -> dict[str, str]:
    key = os.environ.get("LDA_API_KEY", "").strip()
    return {"Authorization": f"Token {key}"} if key else {}


def _token_targets(name: str, aliases: list[str]) -> set[tuple[str, ...]]:
    """Build the set of token-sequences a filing's client name must start with."""
    targets = {tuple(normalize_name(s).split()) for s in [name, *aliases]}
    targets.discard(())
    return targets


def _client_matches(client_name: str, targets: set[tuple[str, ...]]) -> bool:
    """True if the normalized client name *begins with* any target token-sequence.

    Leading-match (not substring) is deliberate: it accepts "exxon mobil corp"
    and "exxon mobil corporation" for target ("exxon","mobil"), while rejecting
    "us apple association" and "twin metals minnesota" (which start with other
    tokens) for "apple" / "meta platforms".
    """
    ct = tuple(normalize_name(client_name).split())
    return any(ct[: len(t)] == t for t in targets)


def fetch_client_total(
    client_name: str,
    aliases: list[str],
    year: int,
    *,
    sleep: float = 1.0,
    max_pages: int = 20,
) -> tuple[float, int]:
    """Return (total_spend_usd, n_filings) attributable to this client for `year`.

    Sums `income`/`expenses` across all matching filings. Because LDA client
    names are inconsistent (CORP vs CORPORATION, punctuation, one-word variants)
    and searches over-match (e.g. "Meta" -> "Twin Metals"), filings are filtered
    by token-prefix against `name` + `aliases`. Curate aliases per entity to
    capture lobbying-specific names (e.g. Alphabet lobbies as "Google ...").
    """
    targets = _token_targets(client_name, aliases)

    total = 0.0
    matched = 0
    # Issue one search per target token-sequence so distinct lobbying names
    # (e.g. "Exxon Mobil" and "ExxonMobil") are each surfaced, then de-dup by
    # filing UUID and filter precisely.
    seen_filings: set[str] = set()
    queries = {t[0] for t in targets if t}
    for q in queries:
        next_url: str | None = build_url(
            API_BASE, {"client_name": q, "filing_year": str(year), "page_size": "100"},
        )
        page = 0
        while next_url and page < max_pages:
            page += 1
            data = _get(next_url)
            for f in data.get("results", []):
                uuid = f.get("filing_uuid", "")
                if uuid in seen_filings:
                    continue
                client = (f.get("client") or {}).get("name", "")
                if not _client_matches(client, targets):
                    continue
                amount = f.get("income") or f.get("expenses") or 0
                try:
                    total += float(amount)
                except (TypeError, ValueError):
                    continue
                seen_filings.add(uuid)
                matched += 1
            next_url = data.get("next")
            if next_url:
                time.sleep(sleep)
    return total, matched


def _get(url: str) -> dict:
    # get_json doesn't take headers; inline a header-aware call only if a key is set.
    headers = _auth_headers()
    if not headers:
        return get_json(url)  # type: ignore[return-value]
    import json
    import urllib.request
    req = urllib.request.Request(url, headers={"User-Agent": "AccountabilityLedger/1.0", **headers})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _read_companies(entities_path: Path) -> list[dict]:
    with open(entities_path, encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    return [r for r in rows if r.get("type", "company").strip() == "company"]


def run(entities_path: Path, raw_dir: Path, year: int, sleep: float) -> Path:
    companies = _read_companies(entities_path)
    out_dir = raw_dir / "senate_lda"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "lobbying.csv"

    rows = []
    for c in companies:
        name = c.get("name", "").strip()
        ticker = c.get("ticker", "").strip().upper()
        aliases = [a.strip() for a in c.get("aliases", "").split(";") if a.strip()]
        if not name:
            continue
        try:
            total, n = fetch_client_total(name, aliases, year, sleep=sleep)
        except Exception as e:
            log.error("LDA fetch failed for %s: %s", name, e)
            continue
        log.info("%-32s $%s across %d filing(s)", name, f"{total:,.0f}", n)
        if n == 0:
            continue  # no filings -> leave unrated rather than write a misleading $0
        rows.append({
            "Client": name,
            "Ticker": ticker,
            "Total Lobbying Spend (USD)": f"{total:.2f}",
            "Filings": str(n),
            "Year": str(year),
        })
        time.sleep(sleep)

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["Client", "Ticker", "Total Lobbying Spend (USD)", "Filings", "Year"])
        w.writeheader()
        w.writerows(rows)
    log.info("Wrote %d company lobbying totals to %s", len(rows), out_path)
    return out_path


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--entities", default="data/entities.csv")
    p.add_argument("--raw-dir", default="data/raw")
    p.add_argument("--year", type=int, default=2024, help="Filing year to aggregate (default: 2024)")
    p.add_argument("--sleep", type=float, default=1.0, help="Seconds between requests (rate-limit friendly)")
    p.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    args = p.parse_args()
    logging.basicConfig(level=getattr(logging, args.log_level), format="%(levelname)s %(name)s — %(message)s")

    entities = Path(args.entities)
    if not entities.exists():
        print(f"ERROR: {entities} not found. Copy data/entities_template.csv first.", file=sys.stderr)
        return 1
    run(entities, Path(args.raw_dir), args.year, args.sleep)
    return 0


if __name__ == "__main__":
    sys.exit(main())
