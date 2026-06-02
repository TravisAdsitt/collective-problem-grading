# The Accountability Ledger

A sourced, domain-by-domain "sniff test" of major U.S. companies (S&P 500)
and top Americans — who is net-positive, net-negative, or mixed on the world's
largest problems, based on **documented actions, not pledges**.

**One rule that separates this from greenwashing aggregators:**
Weight actions over pledges, everywhere. Lobbying records, capital allocation,
and verified outcomes determine stance — not sustainability statements.

---

## Quick start

```bash
# 1. Copy the entity template to your working entity list
cp data/entities_template.csv data/entities.csv
# Edit data/entities.csv — add/remove companies and individuals as needed.

# 2. Download raw source data
#    See data/raw/README.md for per-source instructions.
#    The pipeline does not fail on missing sources — unrated is the fallback.

# 3. Run the pipeline
python -m pipeline.run

# 4. Open the frontend
open frontend/index.html   # macOS
# or just open the file in any browser
```

---

## Repository structure

```
pipeline/
  schema.py          — data models (EntityRecord, DomainScore, Evidence)
  run.py             — CLI entry point
  ingest/            — one file per source; reads from data/raw/<source>/
    influencemap.py
    cdp.py
    sbti.py
    access_to_medicine.py
    fli_ai_safety.py
    ranking_digital_rights.py
    just_capital.py
    sec_ceo_pay.py
    opensecrets.py
    propublica_irs.py
    tax_justice.py
  normalize/         — maps raw source values → common stance/confidence/gap
    climate.py       — InfluenceMap primary; CDP + SBTi secondary
    health.py        — Access to Medicine Index
    ai_safety.py     — FLI AI Safety Index (conflict disclosed)
    digital_rights.py — Ranking Digital Rights
    labor.py         — CEO pay ratio + JUST Capital
    tax_governance.py — Tax Justice Network + OpenSecrets + ProPublica
  assemble/
    matcher.py       — entity matching by ticker then normalized name
    assembler.py     — runs all ingesters + normalizers → EntityRecord list

data/
  entities_template.csv   — seed entity list (copy → entities.csv to use)
  raw/
    README.md        — download instructions per source
    <source>/        — place downloaded CSVs here (gitignored)
  output/
    ledger.json      — generated output (gitignored)

frontend/
  index.html         — browsable single-page app (no build step)
  src/
    app.js
    style.css
```

---

## Output schema

Each entity record in `data/output/ledger.json`:

```json
{
  "entity_id": "AAPL",
  "name": "Apple Inc.",
  "type": "company",
  "ticker": "AAPL",
  "sector": "Technology",
  "domains": {
    "climate": {
      "stance": "net_positive | mixed | net_negative | unrated",
      "confidence": "high | medium | low",
      "pledge_vs_action_gap": "none | moderate | severe | unknown",
      "evidence": [
        {
          "source": "InfluenceMap",
          "metric": "Climate Lobbying Band",
          "value": "B+",
          "url": "https://influencemap.org/...",
          "as_of": "2024-11"
        }
      ]
    }
    // ...one block per domain
  },
  "last_updated": "2025-06-01",
  "notes": ""
}
```

Every `stance` traces to at least one `evidence` item.
`pledge_vs_action_gap` is a first-class field, not a footnote.

---

## Domain sources and data confidence

| Domain | Primary sources | Confidence |
|---|---|---|
| Climate | InfluenceMap (lobbying), CDP, SBTi | **High** |
| Health | Access to Medicine Index | **High** (pharma only) |
| AI Safety | FLI AI Safety Index* | **Medium** |
| Digital Rights | Ranking Digital Rights | **Medium** |
| Labor | SEC CEO Pay Ratio, JUST Capital | **Low–Medium** |
| Tax & Governance | Tax Justice Network, OpenSecrets, ProPublica IRS Files | **Medium** |

\* **Conflict disclosure:** Anthropic scores highest in the FLI AI Safety Index.
Anthropic builds Claude, which assisted in building this project. Treat AI safety
scores with appropriate skepticism and cross-reference with alternative assessments.

---

## Methodology

### Actions over pledges

InfluenceMap is the primary signal for climate because it scores actual political
behavior — lobbying positions and funding. CDP and SBTi are secondary. The
~80% overlap between the 25 worst InfluenceMap scorers and companies with net-zero
pledges is the canonical proof that pledges do not filter.

### Pledge-vs-action gap

`pledge_vs_action_gap` values:
- **severe** — public commitment contradicted by documented action (e.g., net-zero
  pledge + active climate lobbying against policy)
- **moderate** — partial follow-through; pledges exceed verified action
- **none** — actions match or exceed stated commitments
- **unknown** — insufficient data

### No blended score

Domains are kept separate and the spread shown. A company that is excellent on
climate and terrible on labor is represented exactly that way — averaging hides it.

### Documented behavior only for individuals

For Phase 2 (Forbes 400 seed list), only documented facts appear:
political donations, effective tax rates, foundation payout rates. Reader draws
conclusions. This is the liability firewall.

---

## Adding a new source

1. Create `pipeline/ingest/<source_name>.py` inheriting `BaseIngester`.
2. Document the expected CSV columns and download URL in the module docstring.
3. Add download instructions to `data/raw/README.md`.
4. Write a normalizer in `pipeline/normalize/<domain>.py` (or extend an existing one).
5. Wire it into `Assembler._load_indexes()` and the relevant `_score_*` method.

---

## Refresh cadence

Quarterly: check each source for a new edition; re-run affected domain only.
Annual sources: CDP (scores released Jan–Feb), SBTi (rolling), InfluenceMap
(updated regularly), Access to Medicine (every 2 years), FLI AI Safety (semi-annual).

---

## Phase 2 — Individuals

Copy `data/entities_template.csv` and add rows with `type=individual`.
Sources: ProPublica IRS Files (tax conduct), OpenSecrets (political spending),
foundation payout rates from Form 990s via ProPublica Nonprofit Explorer.
All stances for individuals except `tax_governance` will be `unrated` until
individual-level scoring is added for other domains.
