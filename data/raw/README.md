# Raw Data Download Instructions

Each source publishes annual data. Download the relevant file and place it at
the path listed below **before** running the pipeline.

Most files are CSVs or Excel exports. Column names must match what the ingester
expects — see the corresponding `pipeline/ingest/<source>.py` docstring for
the exact column list. If a source exports different column names, either rename
the columns in the file or update the ingester.

---

## Climate / Environment

### InfluenceMap
- **URL:** https://influencemap.org/scores
- **File:** `data/raw/influencemap/company_scores.csv`
- **Columns required:** `Company Name, Ticker, Sector, Band, Performance Score, Influence Score, As Of`
- **Notes:** Band is A+ through F. This is the primary action-over-pledges signal for climate.

### CDP (Carbon Disclosure Project)
- **URL:** https://www.cdp.net/en/scores (requires free registration for full dataset)
- **A-List only (public):** https://www.cdp.net/en/companies/companies-scores
- **File:** `data/raw/cdp/scores.csv`
- **Columns required:** `Account Name, Primary Ticker, Industry (Megasector), CDP Score, Response Year`

### Science Based Targets initiative (SBTi)
- **URL:** https://sciencebasedtargets.org/companies-taking-action (CSV download button on page)
- **File:** `data/raw/sbti/targets.csv`
- **Columns required:** `Company Name, Ticker, ISIN, Sector, Status, Target Year, Near-Term Target, Long-Term Target, Date Published`
- **Notes:** Only "Approved" status counts as verified action. "Committed" = pledge only.

---

## Health / Medicine Access

### Access to Medicine Index
- **URL:** https://accesstomedicine.org/amindex/ (data download on index page)
- **File:** `data/raw/access_to_medicine/rankings.csv`
- **Columns required:** `Rank, Company, Overall Score, R&D Score, Pricing Score, Manufacturing & Supply Score, Patents & Licensing Score, Governance Score, Edition Year`
- **Scope:** Pharmaceutical/biotech companies only. All others will be unrated.

---

## AI Safety & Tech Harms

### FLI AI Safety Index
- **URL:** https://aisafetyindex.net/
- **File:** `data/raw/fli_ai_safety/scores.csv`
- **Columns required:** `Company, Overall Grade, Safety Culture Grade, Transparency Grade, Avoiding Extreme Harms Grade, Alignment Research Grade, Edition`
- **Scope:** ~8 frontier AI labs only. All others unrated.
- **Conflict disclosure:** Anthropic scores highest; Anthropic builds Claude (used in this project).
  Alternative/supplementary sources: AI Now Institute, Center for AI Safety.

---

## Digital Rights / Information Integrity

### Ranking Digital Rights
- **URL:** https://rankingdigitalrights.org/index/
- **File:** `data/raw/ranking_digital_rights/scores.csv`
- **Columns required:** `Company, Ticker, Type, Overall Score, Governance Score, Freedom of Expression Score, Privacy Score, Edition Year`
- **Scope:** Major internet platforms and telecom companies.

---

## Labor & Inequality

### JUST Capital
- **URL:** https://justcapital.com/rankings/ (CSV download available on rankings page)
- **File:** `data/raw/just_capital/rankings.csv`
- **Columns required:** `Rank, Company, Ticker, Industry, Overall Score, Workers Score, Communities Score, Environment Score, Ranking Year`

### SEC CEO-to-Worker Pay Ratio
- **Primary source:** SEC EDGAR DEF 14A proxy filings — search per company at https://efts.sec.gov/LATEST/search-index?q=%22CEO+Pay+Ratio%22&dateRange=custom
- **Aggregated source (easier):** AFL-CIO Executive Paywatch: https://aflcio.org/paywatch
- **File:** `data/raw/sec_ceo_pay/ratios.csv`
- **Columns required:** `Company, Ticker, CEO Name, CEO Total Compensation (USD), Median Worker Pay (USD), Pay Ratio, Fiscal Year`
- **Notes:** Pay Ratio format: `N:1` (e.g. `344:1`)

---

## Tax & Governance

### Tax Justice Network
- **URL:** https://www.taxjustice.net/topics/corporate-tax/corporate-tax-haven-index/
- **File:** `data/raw/tax_justice/corporate_scores.csv`
- **Columns required:** `Company, Ticker, Country of Incorporation, Effective Tax Rate (%), Statutory Rate Comparison (%), Offshore Subsidiaries Count, Haven Score (0–100), Year`

### Federal lobbying — Senate LDA (replaces OpenSecrets API, discontinued 2025-04-15)
- **Generated, not hand-downloaded.** Run the fetcher (no API key needed):
  ```
  python3 -m pipeline.fetch.senate_lda --year 2024
  ```
- **File:** `data/raw/senate_lda/lobbying.csv` — columns: `Client, Ticker, Total Lobbying Spend (USD), Filings, Year`
- **Note:** New entities that come back with $0 lobby under a different client
  name — add it to the `aliases` column in your entity CSV.

### PAC / individual contributions — FEC API (not yet wired)
- **URL:** https://api.open.fec.gov (free key; `DEMO_KEY` for testing). Fetcher TBD.

### ProPublica IRS Files (individuals only)
- **URL:** https://projects.propublica.org/tax-cuts-and-jobs-act/ and https://projects.propublica.org/nonprofits/
- **File:** `data/raw/propublica_irs/individuals.csv`
- **Columns required:** `Name, Net Worth Estimate (USD), Estimated Income (USD), Estimated Federal Tax Rate (%), Statutory Top Rate (%), Tax Rate Gap (pp), Foundation Payout Rate (%), Foundation Name, Source Notes, Year`
- **Notes:** Values derived from ProPublica's published reporting. Cite specific articles in Source Notes column.

---

## Directory structure after downloading

```
data/raw/
  influencemap/
    company_scores.csv
  cdp/
    scores.csv
  sbti/
    targets.csv
  access_to_medicine/
    rankings.csv
  fli_ai_safety/
    scores.csv
  ranking_digital_rights/
    scores.csv
  just_capital/
    rankings.csv
  sec_ceo_pay/
    ratios.csv
  senate_lda/          # generated by: python3 -m pipeline.fetch.senate_lda
    lobbying.csv
  propublica_irs/
    individuals.csv
  tax_justice/
    corporate_scores.csv
```

Sources with missing files produce `"unrated"` stances for the affected domain —
the pipeline does not fail on missing sources.
