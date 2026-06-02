"""
Health / medicine access domain normalization.

Source: Access to Medicine Index (pharma companies only).
Data confidence: HIGH for covered companies; all others are UNRATED.

Stance by rank tier (20 companies assessed):
  Rank 1–5:   net_positive
  Rank 6–12:  mixed
  Rank 13–20: net_negative

Pledge-vs-action gap: the 2024 index found "comprehensive policies" outpacing
implementation — governance scores (pledges) routinely exceed manufacturing
and pricing scores (action). Gap is derived by comparing governance vs. pricing+supply.
"""
from __future__ import annotations
from pipeline.schema import DomainScore, Gap
from .base import make_evidence, stance_from_tier

_TOTAL_RANKED = 20


def _score_gap(governance: float | None, action: float | None) -> Gap:
    """Compare governance (pledge) score against average of action scores."""
    if governance is None or action is None:
        return "unknown"
    diff = governance - action
    if diff >= 20:
        return "severe"
    if diff >= 8:
        return "moderate"
    return "none"


def _safe_float(s: str) -> float | None:
    try:
        return float(s.replace(",", "").strip())
    except (ValueError, AttributeError):
        return None


def normalize(atm_record: dict | None) -> DomainScore:
    if not atm_record:
        return DomainScore.unrated()

    rank_str = atm_record.get("rank", "")
    try:
        rank = int(rank_str)
    except (ValueError, TypeError):
        return DomainScore.unrated()

    stance = stance_from_tier(rank, _TOTAL_RANKED)

    governance = _safe_float(atm_record.get("governance_score", ""))
    pricing = _safe_float(atm_record.get("pricing_score", ""))
    manufacturing = _safe_float(atm_record.get("manufacturing_score", ""))

    action_avg: float | None = None
    if pricing is not None and manufacturing is not None:
        action_avg = (pricing + manufacturing) / 2

    gap = _score_gap(governance, action_avg)

    evidence = [make_evidence(
        source="Access to Medicine Index",
        metric="Overall Rank",
        value=f"#{rank} of {_TOTAL_RANKED}",
        url=atm_record.get("url", "https://accesstomedicine.org/amindex/"),
        as_of=atm_record.get("as_of", ""),
    )]
    if atm_record.get("overall_score"):
        evidence.append(make_evidence(
            source="Access to Medicine Index",
            metric="Overall Score",
            value=atm_record["overall_score"],
            url=atm_record.get("url", "https://accesstomedicine.org/amindex/"),
            as_of=atm_record.get("as_of", ""),
        ))

    return DomainScore(
        stance=stance,
        confidence="high",
        pledge_vs_action_gap=gap,
        evidence=evidence,
    )
