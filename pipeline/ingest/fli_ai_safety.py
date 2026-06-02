"""
Future of Life Institute (FLI) AI Safety Index.

Download: https://aisafetyindex.net/
File to place: data/raw/fli_ai_safety/scores.csv

Expected columns:
  Company, Overall Grade (A|B|C|D|F),
  Safety Culture Grade, Transparency Grade,
  Avoiding Extreme Harms Grade, Alignment Research Grade,
  Edition (e.g. "Winter 2025")

Scope: frontier AI labs only (currently ~8 companies assessed).
Conflict disclosure: Anthropic is the highest-ranked company in the Winter 2025 index.
Anthropic also builds Claude, which assists in drafting this Ledger. Treat with
appropriate skepticism; cross-reference with independent AI safety assessments.
Winter 2025 finding: NO company scored above a D on existential safety — second edition in a row.
"""
from typing import Iterator
from .base import BaseIngester

# Companies outside this set are unrated in this domain.
ASSESSED_COMPANIES = {
    "Anthropic", "Google DeepMind", "Meta AI", "Microsoft", "OpenAI",
    "Amazon", "Apple", "xAI",
}


class FLIAISafetyIngester(BaseIngester):
    source_name = "fli_ai_safety"

    def ingest(self) -> Iterator[dict]:
        for row in self._csv_rows("scores.csv"):
            yield {
                "source": "FLI AI Safety Index",
                "name": row.get("Company", "").strip(),
                "overall_grade": row.get("Overall Grade", "").strip(),
                "safety_culture_grade": row.get("Safety Culture Grade", "").strip(),
                "transparency_grade": row.get("Transparency Grade", "").strip(),
                "extreme_harms_grade": row.get("Avoiding Extreme Harms Grade", "").strip(),
                "alignment_research_grade": row.get("Alignment Research Grade", "").strip(),
                "as_of": row.get("Edition", "").strip(),
                "url": "https://aisafetyindex.net/",
                "conflict_note": (
                    "Anthropic scores highest; Anthropic also builds Claude used in this project. "
                    "See §9 of methodology."
                ),
            }
