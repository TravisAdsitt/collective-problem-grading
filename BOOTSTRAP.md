# Data Source Bootstrap Guide

How to get each source's data into the pipeline. Written after testing network
access from the remote execution environment (blocked) and assessing each source
from a regular machine.

---

## TL;DR — recommended order

Do these first; they're clean CSV downloads with no friction:

1. SBTi
2. JUST Capital
3. Ranking Digital Rights
4. OpenSecrets (free API key, then add HTTP ingester)
5. CDP (free registration, then bulk download)
6. AFL-CIO Paywatch → `data/raw/sec_ceo_pay/ratios.csv`
7. InfluenceMap (email them for data, or use their scraper — see below)
8. Access to Medicine Index + FLI AI Safety Index (small enough to enter manually)
9. ProPublica IRS Files (investigative reporting, no dataset — manual entry only)
10. Tax Justice Network (PDF reports — manual entry or contact them)

---

## Per-source detail

### InfluenceMap (climate lobbying)
- **File:** `data/raw/influencemap/company_scores.csv`
- **Access:** No public bulk download.
  - Option A (preferred): Email their team at info@influencemap.org — they share
    data with researchers and journalists.
  - Option B: Scrape company profile pages at `https://influencemap.org/company/<Name>`.
    Claude can write this scraper.
- **Status:** `[ ]` not yet downloaded
- **Follow-up needed:** Contact them or add scraper

### CDP (Carbon Disclosure Project)
- **File:** `data/raw/cdp/scores.csv`
- **Access:** Free registration required for the full scored dataset.
  Register at https://www.cdp.net/en/scores
  The public A-List page lists top companies but has no bulk CSV.
- **Status:** `[ ]` not yet downloaded
- **Follow-up needed:** Register, request dataset download

### SBTi (Science Based Targets initiative)
- **File:** `data/raw/sbti/targets.csv`
- **Access:** Direct CSV download — no registration required.
  Go to https://sciencebasedtargets.org/companies-taking-action and click
  the CSV download button.
- **Status:** `[ ]` not yet downloaded
- **Follow-up needed:** Just download it

### Access to Medicine Index
- **File:** `data/raw/access_to_medicine/rankings.csv`
- **Access:** Excel file published on their site at https://accesstomedicine.org/amindex/
  Only 20 companies are assessed — small enough to enter manually if the
  Excel export doesn't map cleanly to the expected columns.
- **Status:** `[ ]` not yet downloaded
- **Follow-up needed:** Download Excel, verify column names match ingester

### FLI AI Safety Index
- **File:** `data/raw/fli_ai_safety/scores.csv`
- **Access:** Published as a PDF report at https://aisafetyindex.net/
  Only ~8 companies assessed (Anthropic, Google DeepMind, Meta AI, Microsoft,
  OpenAI, Amazon, Apple, xAI). Small enough to enter manually.
- **Status:** `[ ]` not yet downloaded
- **Conflict note:** Anthropic scores highest; Anthropic builds Claude.
  Disclosed in pipeline and frontend.
- **Follow-up needed:** Read PDF, enter manually as CSV

### Ranking Digital Rights
- **File:** `data/raw/ranking_digital_rights/scores.csv`
- **Access:** CSV download available on their index page at
  https://rankingdigitalrights.org/index/
- **Status:** `[ ]` not yet downloaded
- **Follow-up needed:** Just download it

### JUST Capital
- **File:** `data/raw/just_capital/rankings.csv`
- **Access:** CSV download on their rankings page at https://justcapital.com/rankings/
- **Status:** `[ ]` not yet downloaded
- **Follow-up needed:** Just download it

### SEC CEO-to-Worker Pay Ratio
- **File:** `data/raw/sec_ceo_pay/ratios.csv`
- **Access:** No single bulk source. Best options:
  - AFL-CIO Executive Paywatch publishes an annual spreadsheet at
    https://aflcio.org/paywatch — easiest aggregate source.
  - Economic Policy Institute also publishes pay ratio analysis.
  - Raw filings: EDGAR full-text search at https://efts.sec.gov/LATEST/search-index
    (search "CEO Pay Ratio" in DEF 14A filings) — per-company, labor-intensive.
- **Status:** `[ ]` not yet downloaded
- **Follow-up needed:** Download AFL-CIO Paywatch spreadsheet, map columns

### Federal lobbying — Senate LDA (replaces OpenSecrets)
- **File:** `data/raw/senate_lda/lobbying.csv`
- **⚠️ OpenSecrets API discontinued 2025-04-15.** It was only ever a roll-up of
  primary federal filings, so we now pull straight from the source.
- **Access:** Senate LDA API — **no key required** (register for a key only to
  raise rate limits, then set `LDA_API_KEY`). Just run the fetcher:
  ```
  python3 -m pipeline.fetch.senate_lda --year 2024
  ```
  It reads your `data/entities.csv`, aggregates each company's annual lobbying
  spend (filtering by token-prefix on name + `aliases` to exclude false hits),
  and writes the CSV the ingester reads.
- **Status:** `[x]` working — fetcher built and verified against 2024 data.
- **Follow-up needed:** For new entities, check the log: a $0/0-filings result
  means the company lobbies under a different name — add it to the `aliases`
  column (e.g. Alphabet → `Google`, Exxon → `ExxonMobil`).

### PAC + individual political contributions — FEC (not yet wired)
- **Access:** FEC API at https://api.open.fec.gov — free key (or `DEMO_KEY` for
  testing). This is the other half of what OpenSecrets used to provide.
- **Status:** `[ ]` reachability confirmed; fetcher not yet built.
- **Follow-up needed:** Ask Claude to "add the FEC contributions fetcher."

### ProPublica IRS Files (individuals — tax rates)
- **File:** `data/raw/propublica_irs/individuals.csv`
- **Access:** The "IRS Files" data was published through investigative journalism,
  not as a public dataset. No download exists.
  Must manually enter data from ProPublica's published articles:
  https://www.propublica.org/series/the-irs-files
  Cite each article as the source in the `source_notes` column.
- **Status:** `[ ]` manual entry required
- **Follow-up needed:** Read articles, enter manually for individuals of interest

### ProPublica Nonprofit Explorer (foundation payout rates)
- **Not yet wired into a separate ingester** — currently folded into the
  ProPublica IRS ingester.
- **Access:** Fully open API, no key required.
  `https://projects.propublica.org/nonprofits/api/v2/search.json?q=<foundation name>`
  Claude can write an HTTP ingester for this.
- **Follow-up needed:** Claude adds HTTP ingester for foundation payout rates

### Tax Justice Network
- **File:** `data/raw/tax_justice/corporate_scores.csv`
- **Access:** Data published in PDF reports. No machine-readable bulk export.
  Contact them at https://www.taxjustice.net/contact/ — they may share data
  for research purposes.
- **Status:** `[ ]` not yet available
- **Follow-up needed:** Contact TJN or enter manually from their published tables

---

## Things Claude can build when you're ready

- **InfluenceMap scraper** — scrape company profile pages, output CSV matching
  the expected ingester format
- **OpenSecrets HTTP ingester** — replace the CSV reader with direct API calls
  using your key
- **ProPublica Nonprofit Explorer ingester** — fetch foundation payout rates
  from the open API
- **PDF extractor** — use `pdfplumber` (already in optional requirements) to
  pull tables from FLI and Access to Medicine PDF reports automatically

To kick off any of these, just ask: "add the OpenSecrets HTTP ingester" etc.

---

## Network note

This pipeline **cannot reach external hosts from the Claude Code remote
container** — the network policy only allows package registries (PyPI, npm).
All data downloads and scraping must run on your local machine.
Once you have CSV files in `data/raw/<source>/`, run `python -m pipeline.run`
locally to produce `data/output/ledger.json`, then open `frontend/index.html`.
