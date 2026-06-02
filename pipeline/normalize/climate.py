"""
Climate domain normalization.

Sources combined: InfluenceMap (lobbying), CDP (disclosure), SBTi (targets).
Data confidence: HIGH.

Stance logic (actions over pledges):
  InfluenceMap is primary — it measures actual political behavior.
  CDP and SBTi are secondary confirmers.

  net_positive:  InfluenceMap A/A+ AND (CDP A or SBTi Approved)
  mixed:         InfluenceMap B–C OR conflicting signals between sources
  net_negative:  InfluenceMap D/E/F (regardless of pledges — this is the sniff test)

Pledge-vs-action gap:
  severe:   InfluenceMap D/E/F + has a net-zero/SBTi Committed pledge
  moderate: InfluenceMap C + SBTi Committed but not Approved
  none:     InfluenceMap A/A+ + SBTi Approved
  unknown:  insufficient data
"""
from __future__ import annotations
from pipeline.schema import DomainScore, Evidence, Stance, Gap
from .base import letter_to_stance, make_evidence


# InfluenceMap band → effective climate lobbying stance
_IM_STANCE: dict[str, Stance] = {
    "A+": "net_positive", "A": "net_positive", "A-": "net_positive",
    "B+": "mixed",        "B": "mixed",        "B-": "mixed",
    "C+": "mixed",        "C": "mixed",        "C-": "net_negative",
    "D+": "net_negative", "D": "net_negative",
    "E":  "net_negative", "F": "net_negative",
}

# SBTi statuses that represent COMMITTED pledges (not yet verified action)
_SBTI_PLEDGE_STATUSES = {"Committed", "Targets Set"}
# SBTi statuses that represent VERIFIED ACTION
_SBTI_ACTION_STATUSES = {"Approved", "Achieved"}


def normalize(
    im_record: dict | None,
    cdp_record: dict | None,
    sbti_record: dict | None,
) -> DomainScore:
    evidence: list[Evidence] = []
    im_stance: Stance = "unrated"
    cdp_stance: Stance = "unrated"
    sbti_is_pledge = False
    sbti_is_action = False

    if im_record:
        band = im_record.get("band", "")
        im_stance = _IM_STANCE.get(band, "unrated")
        evidence.append(make_evidence(
            source="InfluenceMap",
            metric="Climate Lobbying Band",
            value=band,
            url=im_record.get("url", "https://influencemap.org"),
            as_of=im_record.get("as_of", ""),
        ))
        perf = im_record.get("performance_score", "")
        if perf:
            evidence.append(make_evidence(
                source="InfluenceMap",
                metric="Performance Score",
                value=perf,
                url=im_record.get("url", "https://influencemap.org"),
                as_of=im_record.get("as_of", ""),
            ))

    if cdp_record:
        cdp_score = cdp_record.get("score", "")
        cdp_stance = letter_to_stance(cdp_score)
        evidence.append(make_evidence(
            source="CDP",
            metric="CDP Climate Score",
            value=cdp_score,
            url=cdp_record.get("url", "https://www.cdp.net/en/companies/companies-scores"),
            as_of=cdp_record.get("as_of", ""),
        ))

    if sbti_record:
        status = sbti_record.get("status", "")
        sbti_is_pledge = status in _SBTI_PLEDGE_STATUSES
        sbti_is_action = status in _SBTI_ACTION_STATUSES
        evidence.append(make_evidence(
            source="SBTi",
            metric="Target Status",
            value=status,
            url=sbti_record.get("url", "https://sciencebasedtargets.org"),
            as_of=sbti_record.get("as_of", ""),
        ))

    # Derive overall stance — InfluenceMap is primary (action over pledges)
    if im_stance != "unrated":
        stance = im_stance
    elif cdp_stance != "unrated":
        stance = cdp_stance
    elif sbti_is_action:
        stance = "mixed"  # action on targets but no lobbying data — can't fully confirm
    else:
        stance = "unrated"

    # Derive pledge-vs-action gap
    gap: Gap = "unknown"
    if im_stance == "net_negative" and (sbti_is_pledge or sbti_is_action or cdp_stance in ("net_positive", "mixed")):
        gap = "severe"   # lobbying against climate policy while pledging targets
    elif im_stance == "net_negative" and cdp_stance == "unrated" and not sbti_record:
        gap = "unknown"
    elif im_stance in ("mixed",) and sbti_is_pledge and not sbti_is_action:
        gap = "moderate"
    elif im_stance == "net_positive" and sbti_is_action:
        gap = "none"
    elif im_stance == "net_positive" and not sbti_record:
        gap = "moderate"  # good lobbying stance but no verified target

    if not evidence:
        return DomainScore.unrated()

    return DomainScore(
        stance=stance,
        confidence="high",
        pledge_vs_action_gap=gap,
        evidence=evidence,
    )
