"""
Core data models for the Accountability Ledger.

Every stance must trace to at least one Evidence item.
pledge_vs_action_gap is a first-class field, not a footnote.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Literal
import json

Stance = Literal["net_positive", "mixed", "net_negative", "unrated"]
Confidence = Literal["high", "medium", "low"]
Gap = Literal["none", "moderate", "severe", "unknown"]


@dataclass
class Evidence:
    source: str
    metric: str
    value: str
    url: str
    as_of: str  # YYYY-MM


@dataclass
class DomainScore:
    stance: Stance
    confidence: Confidence
    pledge_vs_action_gap: Gap
    evidence: list[Evidence] = field(default_factory=list)

    @classmethod
    def unrated(cls) -> "DomainScore":
        return cls(stance="unrated", confidence="low", pledge_vs_action_gap="unknown")


@dataclass
class EntityRecord:
    entity_id: str       # ticker for companies, slug for individuals
    name: str
    type: Literal["company", "individual"]
    ticker: str = ""
    sector: str = ""
    domains: dict[str, DomainScore] = field(default_factory=dict)
    last_updated: str = ""  # YYYY-MM-DD
    notes: str = ""

    def to_dict(self) -> dict:
        d = asdict(self)
        return d

    def to_json(self, **kw) -> str:
        return json.dumps(self.to_dict(), **kw)

    @classmethod
    def from_dict(cls, d: dict) -> "EntityRecord":
        domains = {}
        for k, v in d.get("domains", {}).items():
            evidence = [Evidence(**e) for e in v.get("evidence", [])]
            domains[k] = DomainScore(
                stance=v["stance"],
                confidence=v["confidence"],
                pledge_vs_action_gap=v["pledge_vs_action_gap"],
                evidence=evidence,
            )
        return cls(
            entity_id=d["entity_id"],
            name=d["name"],
            type=d["type"],
            ticker=d.get("ticker", ""),
            sector=d.get("sector", ""),
            domains=domains,
            last_updated=d.get("last_updated", ""),
            notes=d.get("notes", ""),
        )


DOMAINS = [
    "climate",
    "health",
    "ai_safety",
    "digital_rights",
    "labor",
    "tax_governance",
]

DOMAIN_CONFIDENCE: dict[str, Confidence] = {
    "climate": "high",
    "health": "high",
    "ai_safety": "medium",
    "digital_rights": "medium",
    "labor": "low",
    "tax_governance": "medium",
}
