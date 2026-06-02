"""
Labor & inequality domain normalization.

Sources: SEC CEO Pay Ratio (Dodd-Frank §953(b)), JUST Capital rankings.
Data confidence: LOW–MEDIUM.

CEO-to-worker pay ratio thresholds (S&P 500 median ≈ 200:1):
  <= 100:1:   net_positive
  <= 400:1:   mixed
  >  400:1:   net_negative

JUST Capital overall score (0–100):
  >= 60: net_positive
  >= 40: mixed
  <  40: net_negative

When both sources present, take the worse stance (conservative approach).

Pledge-vs-action gap:
  JUST Capital separates governance/policy scores from worker outcome scores.
  Gap = severe if governance >> workers score; otherwise moderate or none.
  For pay ratio: no gap concept (it's a disclosed fact, not a pledge).
"""
from __future__ import annotations
from pipeline.schema import DomainScore, Stance, Gap
from .base import make_evidence, score_to_stance


def _safe_float(s: str) -> float | None:
    try:
        return float(s.replace(",", "").strip())
    except (ValueError, AttributeError):
        return None


def _ratio_to_stance(ratio_str: str) -> Stance:
    """Parse 'N:1' pay ratio string into stance."""
    try:
        n = float(ratio_str.split(":")[0].replace(",", "").strip())
    except (ValueError, IndexError, AttributeError):
        return "unrated"
    if n <= 100:
        return "net_positive"
    if n <= 400:
        return "mixed"
    return "net_negative"


def _worse_stance(a: Stance, b: Stance) -> Stance:
    order = ["net_positive", "mixed", "net_negative", "unrated"]
    ai, bi = (order.index(s) if s in order else 3 for s in (a, b))
    return order[max(ai, bi)]


def normalize(ceo_pay_record: dict | None, just_record: dict | None) -> DomainScore:
    if not ceo_pay_record and not just_record:
        return DomainScore.unrated()

    evidence = []
    pay_stance: Stance = "unrated"
    just_stance: Stance = "unrated"
    gap: Gap = "unknown"

    if ceo_pay_record:
        ratio_str = ceo_pay_record.get("pay_ratio", "")
        pay_stance = _ratio_to_stance(ratio_str)
        evidence.append(make_evidence(
            source="SEC CEO Pay Ratio (DEF 14A)",
            metric="CEO-to-Median-Worker Pay Ratio",
            value=ratio_str,
            url=ceo_pay_record.get("url", "https://www.sec.gov"),
            as_of=ceo_pay_record.get("as_of", ""),
        ))

    if just_record:
        overall_str = just_record.get("overall_score", "")
        overall = _safe_float(overall_str)
        workers_str = just_record.get("workers_score", "")
        workers = _safe_float(workers_str)

        if overall is not None:
            just_stance = score_to_stance(overall, positive_above=60.0, negative_below=40.0)
            evidence.append(make_evidence(
                source="JUST Capital",
                metric="Overall Score",
                value=f"{overall:.1f}/100",
                url=just_record.get("url", "https://justcapital.com/rankings/"),
                as_of=just_record.get("as_of", ""),
            ))
        if workers is not None:
            evidence.append(make_evidence(
                source="JUST Capital",
                metric="Workers Score",
                value=f"{workers:.1f}/100",
                url=just_record.get("url", "https://justcapital.com/rankings/"),
                as_of=just_record.get("as_of", ""),
            ))
            if overall is not None:
                diff = overall - workers
                if diff >= 20:
                    gap = "severe"
                elif diff >= 8:
                    gap = "moderate"
                else:
                    gap = "none"

    stance = _worse_stance(pay_stance, just_stance)
    if stance == "unrated":
        return DomainScore.unrated()

    return DomainScore(
        stance=stance,
        confidence="low",
        pledge_vs_action_gap=gap,
        evidence=evidence,
    )
