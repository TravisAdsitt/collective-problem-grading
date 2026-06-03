"""
AI safety & tech harms domain normalization.

Source: FLI AI Safety Index.
Data confidence: MEDIUM (young methodology, few editions, small set of assessed companies).

Conflict disclosure: Anthropic scores highest; Anthropic builds Claude.
This is disclosed in both the source metadata and the output record.

Stance from overall grade:
  A/A-:       net_positive  (no company has reached this threshold as of Winter 2025)
  B+/B/B-:    mixed
  C+/C/C-:    net_negative  (Winter 2025: all companies D or below on existential safety)
  D+ and below: net_negative

Pledge-vs-action gap: safety commitments vs. capability deployment pace.
Currently: "unknown" for all companies — the index doesn't directly score this
dimension yet; it's flagged for future edition integration.
"""
from __future__ import annotations
from pipeline.schema import DomainScore
from .base import letter_to_stance, make_evidence

_CONFLICT_NOTE = (
    "Conflict: Anthropic scored highest in FLI AI Safety Index Winter 2025. "
    "Anthropic also builds Claude, used in drafting this Ledger. Treat with appropriate skepticism."
)


def normalize(fli_record: dict | None) -> DomainScore:
    if not fli_record:
        return DomainScore.unrated()

    grade = fli_record.get("overall_grade", "")
    stance = letter_to_stance(grade)

    evidence = [make_evidence(
        source="FLI AI Safety Index",
        metric="Overall Grade",
        value=grade or "Not scored",
        url=fli_record.get("url", "https://aisafetyindex.net/"),
        as_of=fli_record.get("as_of", ""),
    )]

    for metric_key, label in [
        ("safety_culture_grade", "Safety Culture Grade"),
        ("transparency_grade", "Transparency Grade"),
        ("extreme_harms_grade", "Avoiding Extreme Harms Grade"),
    ]:
        val = fli_record.get(metric_key, "")
        if val:
            evidence.append(make_evidence(
                source="FLI AI Safety Index",
                metric=label,
                value=val,
                url=fli_record.get("url", "https://aisafetyindex.net/"),
                as_of=fli_record.get("as_of", ""),
            ))

    # Surface the conflict disclosure in the record itself (not just README/frontend)
    # so it travels with Anthropic's AI-safety evidence wherever the data is consumed.
    company = fli_record.get("name", "")
    if "anthropic" in company.lower():
        evidence.append(make_evidence(
            source="FLI AI Safety Index",
            metric="Conflict disclosure",
            value=_CONFLICT_NOTE,
            url=fli_record.get("url", "https://aisafetyindex.net/"),
            as_of=fli_record.get("as_of", ""),
        ))

    return DomainScore(
        stance=stance,
        confidence="medium",
        pledge_vs_action_gap="unknown",
        evidence=evidence,
    )
