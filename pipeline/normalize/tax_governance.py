"""
Tax & governance domain normalization.

Sources:
  Companies — Tax Justice Network (corporate haven scores), OpenSecrets (lobbying spend).
  Individuals — ProPublica IRS Files (effective vs. statutory tax rate, foundation payout).

Data confidence: MEDIUM.

Corporate stance by haven score (0–100, higher = more avoidance):
  haven_score <= 20: net_positive
  haven_score <= 55: mixed
  haven_score >  55: net_negative

Individual stance:
  Effective tax rate within 5pp of statutory rate: net_positive
  5–20pp gap: mixed
  >20pp gap: net_negative

Pledge-vs-action gap (individuals):
  If foundation payout rate < 5% (IRS minimum): severe — philanthropy pledge with minimal distribution.
  5–7%: moderate; >= 7%: none.
  Companies: no pledge concept — lobbying spend is documented action.
"""
from __future__ import annotations
from pipeline.schema import DomainScore, Stance, Gap
from .base import make_evidence


def _safe_float(s: str) -> float | None:
    try:
        return float(s.replace(",", "").replace("%", "").strip())
    except (ValueError, AttributeError):
        return None


def _haven_stance(haven_score: float) -> Stance:
    if haven_score <= 20:
        return "net_positive"
    if haven_score <= 55:
        return "mixed"
    return "net_negative"


def _individual_stance(effective_rate: float, statutory_rate: float) -> Stance:
    gap_pp = statutory_rate - effective_rate
    if gap_pp <= 5:
        return "net_positive"
    if gap_pp <= 20:
        return "mixed"
    return "net_negative"


def _individual_gap(payout_rate: float | None) -> Gap:
    if payout_rate is None:
        return "unknown"
    if payout_rate < 5.0:
        return "severe"
    if payout_rate < 7.0:
        return "moderate"
    return "none"


def normalize_company(
    tax_justice_record: dict | None,
    opensecrets_record: dict | None,
) -> DomainScore:
    if not tax_justice_record and not opensecrets_record:
        return DomainScore.unrated()

    evidence = []
    stance: Stance = "unrated"

    if tax_justice_record:
        haven_str = tax_justice_record.get("haven_score", "")
        haven = _safe_float(haven_str)
        eff_rate = _safe_float(tax_justice_record.get("effective_tax_rate_pct", ""))
        if haven is not None:
            stance = _haven_stance(haven)
            evidence.append(make_evidence(
                source="Tax Justice Network",
                metric="Corporate Haven Score",
                value=f"{haven:.0f}/100",
                url=tax_justice_record.get("url", "https://www.taxjustice.net"),
                as_of=tax_justice_record.get("as_of", ""),
            ))
        if eff_rate is not None:
            evidence.append(make_evidence(
                source="Tax Justice Network",
                metric="Effective Tax Rate",
                value=f"{eff_rate:.1f}%",
                url=tax_justice_record.get("url", "https://www.taxjustice.net"),
                as_of=tax_justice_record.get("as_of", ""),
            ))

    if opensecrets_record:
        lobbying = opensecrets_record.get("total_lobbying_usd", "")
        if lobbying:
            evidence.append(make_evidence(
                source="OpenSecrets / FEC",
                metric="Total Lobbying Spend",
                value=f"${lobbying}",
                url=opensecrets_record.get("url", "https://www.opensecrets.org"),
                as_of=opensecrets_record.get("as_of", ""),
            ))

    if stance == "unrated":
        return DomainScore.unrated()

    return DomainScore(
        stance=stance,
        confidence="medium",
        pledge_vs_action_gap="unknown",  # companies: lobbying is action, no pledge concept
        evidence=evidence,
    )


def normalize_individual(propublica_record: dict | None) -> DomainScore:
    if not propublica_record:
        return DomainScore.unrated()

    effective = _safe_float(propublica_record.get("effective_tax_rate_pct", ""))
    statutory = _safe_float(propublica_record.get("statutory_rate_pct", ""))
    payout = _safe_float(propublica_record.get("foundation_payout_rate_pct", ""))

    if effective is None or statutory is None:
        return DomainScore.unrated()

    stance = _individual_stance(effective, statutory)
    gap = _individual_gap(payout)

    evidence = [make_evidence(
        source="ProPublica IRS Files",
        metric="Effective Federal Tax Rate",
        value=f"{effective:.1f}%",
        url=propublica_record.get("url", "https://projects.propublica.org/tax-cuts-and-jobs-act/"),
        as_of=propublica_record.get("as_of", ""),
    ), make_evidence(
        source="ProPublica IRS Files",
        metric="Statutory Top Rate",
        value=f"{statutory:.1f}%",
        url=propublica_record.get("url", "https://projects.propublica.org/tax-cuts-and-jobs-act/"),
        as_of=propublica_record.get("as_of", ""),
    )]

    if payout is not None:
        evidence.append(make_evidence(
            source="ProPublica IRS Files",
            metric="Foundation Payout Rate",
            value=f"{payout:.1f}%",
            url=propublica_record.get("url", "https://projects.propublica.org/tax-cuts-and-jobs-act/"),
            as_of=propublica_record.get("as_of", ""),
        ))

    return DomainScore(
        stance=stance,
        confidence="medium",
        pledge_vs_action_gap=gap,
        evidence=evidence,
    )
