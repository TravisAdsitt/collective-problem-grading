from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterator
import csv
import json
import logging

log = logging.getLogger(__name__)


class BaseIngester(ABC):
    source_name: str  # must match a subdirectory under data/raw/

    def __init__(self, raw_dir: Path):
        self.raw_dir = raw_dir

    @abstractmethod
    def ingest(self) -> Iterator[dict]:
        """Yield raw source records."""
        ...

    def _csv_rows(self, filename: str) -> list[dict]:
        path = self.raw_dir / self.source_name / filename
        if not path.exists():
            log.warning("Missing raw file: %s — see data/raw/README.md for download instructions", path)
            return []
        with open(path, encoding="utf-8-sig") as f:
            return list(csv.DictReader(f))

    def _json(self, filename: str) -> list | dict:
        path = self.raw_dir / self.source_name / filename
        if not path.exists():
            log.warning("Missing raw file: %s — see data/raw/README.md for download instructions", path)
            return []
        with open(path) as f:
            return json.load(f)
