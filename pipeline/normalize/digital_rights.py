"""
Digital rights / information integrity normalization.

Source: Ranking Digital Rights (RDR).
Data confidence: MEDIUM — measures disclosed policies, not verified outcomes.

Stance from overall score (0–100):
  >= 60: net_positive
  >= 35: mixed
  <  35: net_negative

Pledge-vs-action gap: RDR's governance score measures policies/commitments;
freedom of expression and privacy scores measure disclosure of practices.
A high governance score with low implementation scores signals a gap.
"""
from __future__ import annotations
from pipeline.schema import DomainScore, Gap
from .base import score_to_stance, make_evidence


def _safe_float(s: str) -> float | None:
    try:
        return float(s.replace(",", "").strip())
    except (ValueError, AttributeError):
        return None


def _gap_from_scores(governance: float | None, free_expression: float | None, privacy: float | None) -> Gap:
    if governance is None:
        return "unknown"
    action_scores = [s for s in [free_expression, privacy] if s is not None]
    if not action_scores:
        return "unknown"
    action_avg = sum(action_scores) / len(action_scores)
    diff = governance - action_avg
    if diff >= 20:
        return "severe"
    if diff >= 8:
        return "moderate"
    return "none"


def normalize(rdr_record: dict | None) -> DomainScore:
    if not rdr_record:
        return DomainScore.unrated()

    overall_str = rdr_record.get("overall_score", "")
    overall = _safe_float(overall_str)
    if overall is None:
        return DomainScore.unrated()

    stance = score_to_stance(overall, positive_above=60.0, negative_below=35.0)

    gov = _safe_float(rdr_record.get("governance_score", ""))
    fex = _safe_float(rdr_record.get("free_expression_score", ""))
    priv = _safe_float(rdr_record.get("privacy_score", ""))
    gap = _gap_from_scores(gov, fex, priv)

    evidence = [make_evidence(
        source="Ranking Digital Rights",
        metric="Overall Score",
        value=f"{overall:.1f}/100",
        url=rdr_record.get("url", "https://rankingdigitalrights.org/index/"),
        as_of=rdr_record.get("as_of", ""),
    )]
    if gov is not None:
        evidence.append(make_evidence(
            source="Ranking Digital Rights",
            metric="Governance Score",
            value=f"{gov:.1f}",
            url=rdr_record.get("url", "https://rankingdigitalrights.org/index/"),
            as_of=rdr_record.get("as_of", ""),
        ))

    return DomainScore(
        stance=stance,
        confidence="medium",
        pledge_vs_action_gap=gap,
        evidence=evidence,
    )
