"""
Assembler — merges normalized domain scores into per-entity EntityRecords.

Usage:
  assembler = Assembler(raw_dir=Path("data/raw"))
  records = assembler.run(entity_list_path=Path("data/entities.csv"))
  assembler.write(records, output_path=Path("data/output/ledger.json"))
"""
from __future__ import annotations

import csv
import json
import logging
from datetime import date
from pathlib import Path

from pipeline.schema import EntityRecord, DomainScore, DOMAINS
from pipeline.assemble.matcher import SourceIndex

from pipeline.ingest.influencemap import InfluenceMapIngester
from pipeline.ingest.cdp import CDPIngester
from pipeline.ingest.sbti import SBTiIngester
from pipeline.ingest.access_to_medicine import AccessToMedicineIngester
from pipeline.ingest.fli_ai_safety import FLIAISafetyIngester
from pipeline.ingest.ranking_digital_rights import RankingDigitalRightsIngester
from pipeline.ingest.just_capital import JUSTCapitalIngester
from pipeline.ingest.sec_ceo_pay import SEOCeoPayIngester
from pipeline.ingest.opensecrets import OpenSecretsIngester
from pipeline.ingest.propublica_irs import ProPublicaIRSIngester
from pipeline.ingest.tax_justice import TaxJusticeIngester

import pipeline.normalize.climate as norm_climate
import pipeline.normalize.health as norm_health
import pipeline.normalize.ai_safety as norm_ai_safety
import pipeline.normalize.digital_rights as norm_digital_rights
import pipeline.normalize.labor as norm_labor
import pipeline.normalize.tax_governance as norm_tax

log = logging.getLogger(__name__)


class Assembler:
    def __init__(self, raw_dir: Path):
        self.raw_dir = raw_dir

    def _load_indexes(self) -> dict[str, SourceIndex]:
        """Ingest all sources and build lookup indexes."""
        def idx(ingester_class, **kw) -> SourceIndex:
            records = list(ingester_class(self.raw_dir, **kw).ingest())
            return SourceIndex(records)

        return {
            "influencemap": idx(InfluenceMapIngester),
            "cdp": idx(CDPIngester),
            "sbti": idx(SBTiIngester),
            "access_to_medicine": SourceIndex(
                list(AccessToMedicineIngester(self.raw_dir).ingest()),
                ticker_field="",  # ATM doesn't use tickers
                name_field="name",
            ),
            "fli_ai_safety": SourceIndex(
                list(FLIAISafetyIngester(self.raw_dir).ingest()),
                ticker_field="",
                name_field="name",
            ),
            "rdr": idx(RankingDigitalRightsIngester),
            "just_capital": idx(JUSTCapitalIngester),
            "sec_ceo_pay": idx(SEOCeoPayIngester),
            "opensecrets_lobbying": SourceIndex(
                [r for r in OpenSecretsIngester(self.raw_dir).ingest() if r.get("data_type") == "lobbying"]
            ),
            "propublica": SourceIndex(
                list(ProPublicaIRSIngester(self.raw_dir).ingest()),
                ticker_field="",
                name_field="name",
            ),
            "tax_justice": idx(TaxJusticeIngester),
        }

    def _score_company(self, entity: dict, idx: dict[str, SourceIndex]) -> dict[str, DomainScore]:
        ticker, name = entity["ticker"], entity["name"]

        def get(source_key: str) -> dict | None:
            return idx[source_key].lookup(ticker, name)

        climate = norm_climate.normalize(
            im_record=get("influencemap"),
            cdp_record=get("cdp"),
            sbti_record=get("sbti"),
        )
        health = norm_health.normalize(get("access_to_medicine"))
        ai_safety = norm_ai_safety.normalize(get("fli_ai_safety"))
        digital_rights = norm_digital_rights.normalize(get("rdr"))
        labor = norm_labor.normalize(
            ceo_pay_record=get("sec_ceo_pay"),
            just_record=get("just_capital"),
        )
        tax = norm_tax.normalize_company(
            tax_justice_record=get("tax_justice"),
            opensecrets_record=get("opensecrets_lobbying"),
        )

        return {
            "climate": climate,
            "health": health,
            "ai_safety": ai_safety,
            "digital_rights": digital_rights,
            "labor": labor,
            "tax_governance": tax,
        }

    def _score_individual(self, entity: dict, idx: dict[str, SourceIndex]) -> dict[str, DomainScore]:
        name = entity["name"]

        def get(source_key: str) -> dict | None:
            return idx[source_key].lookup("", name)

        tax = norm_tax.normalize_individual(get("propublica"))

        return {
            "climate": DomainScore.unrated(),
            "health": DomainScore.unrated(),
            "ai_safety": DomainScore.unrated(),
            "digital_rights": DomainScore.unrated(),
            "labor": DomainScore.unrated(),
            "tax_governance": tax,
        }

    def run(self, entity_list_path: Path) -> list[EntityRecord]:
        """
        entity_list_path: CSV with columns: entity_id, name, type, ticker, sector
        """
        if not entity_list_path.exists():
            raise FileNotFoundError(
                f"Entity list not found: {entity_list_path}\n"
                "Create it from data/entities_template.csv — see README.md."
            )

        with open(entity_list_path, encoding="utf-8-sig") as f:
            entities = list(csv.DictReader(f))

        log.info("Loading source indexes...")
        idx = self._load_indexes()

        today = date.today().isoformat()
        records: list[EntityRecord] = []

        for entity in entities:
            entity_type = entity.get("type", "company").strip()
            ticker = entity.get("ticker", "").strip().upper()
            entity_id = ticker or entity.get("entity_id", "").strip()
            name = entity.get("name", "").strip()

            if entity_type == "company":
                domains = self._score_company(entity, idx)
            else:
                domains = self._score_individual(entity, idx)

            records.append(EntityRecord(
                entity_id=entity_id,
                name=name,
                type=entity_type,
                ticker=ticker,
                sector=entity.get("sector", "").strip(),
                domains=domains,
                last_updated=today,
                notes=entity.get("notes", "").strip(),
            ))
            log.debug("Scored %s (%s)", name, entity_id)

        log.info("Assembled %d entity records.", len(records))
        return records

    @staticmethod
    def write(records: list[EntityRecord], output_path: Path) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        payload = [r.to_dict() for r in records]
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
        log.info("Wrote %d records to %s", len(records), output_path)
