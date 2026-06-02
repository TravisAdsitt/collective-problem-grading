"""
Shared normalization utilities.
"""
from pipeline.schema import Stance, Confidence, Gap, Evidence, DomainScore


def make_evidence(source: str, metric: str, value: str, url: str, as_of: str) -> Evidence:
    return Evidence(source=source, metric=metric, value=value, url=url, as_of=as_of)


def stance_from_tier(tier: int, n_tiers: int) -> Stance:
    """Map a 1-based tier rank into a stance (higher tiers = worse performance)."""
    fraction = tier / n_tiers
    if fraction <= 0.25:
        return "net_positive"
    if fraction <= 0.6:
        return "mixed"
    return "net_negative"


def letter_to_stance(grade: str) -> Stance:
    """A+/A/A- → net_positive; B+/B/B-/C+ → mixed; C and below → net_negative."""
    g = grade.strip().upper()
    if g in ("A+", "A", "A-"):
        return "net_positive"
    if g in ("B+", "B", "B-", "C+"):
        return "mixed"
    if g in ("C", "C-", "D+", "D", "D-", "E", "F"):
        return "net_negative"
    return "unrated"


def score_to_stance(score: float, *, low: float = 0.0, high: float = 100.0,
                    positive_above: float = 60.0, negative_below: float = 35.0) -> Stance:
    """Map a numeric score to stance using configurable thresholds."""
    if score >= positive_above:
        return "net_positive"
    if score >= negative_below:
        return "mixed"
    return "net_negative"
