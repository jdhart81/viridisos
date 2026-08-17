"""Read-only ViridisOS intake for published research without product wrappers."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
from typing import Iterable


DEFAULT_PATH = Path(__file__).with_name("research_intake.json")
ALLOWED_STATES = {"BACKLOG_NO_WRAPPER", "ADAPTER_REVIEW", "CERTIFICATION_READY"}


@dataclass(frozen=True)
class ResearchRecord:
    abbreviation: str
    run_id: str
    doi: str
    successor_version_candidate: str
    state: str
    product_line: str
    spine_admitted: bool

    @property
    def has_product_wrapper(self) -> bool:
        return self.state in {"ADAPTER_REVIEW", "CERTIFICATION_READY"}

    @property
    def certification_ready(self) -> bool:
        return self.state == "CERTIFICATION_READY"


class ResearchRegistry:
    def __init__(self, path: Path = DEFAULT_PATH):
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload.get("standard") != "VOS-RESEARCH-INTAKE-1":
            raise ValueError("invalid research intake standard")
        rows = payload.get("records")
        if not isinstance(rows, list):
            raise ValueError("research intake records must be an array")
        records: list[ResearchRecord] = []
        seen: set[str] = set()
        for row in rows:
            record = ResearchRecord(**row)
            if record.state not in ALLOWED_STATES:
                raise ValueError(f"invalid research intake state: {record.state}")
            if re.fullmatch(r"10\.\d{4,9}/zenodo\.\d+", record.doi) is None:
                raise ValueError(f"invalid research DOI: {record.doi}")
            if record.abbreviation in seen:
                raise ValueError(f"duplicate research abbreviation: {record.abbreviation}")
            seen.add(record.abbreviation)
            records.append(record)
        self._records = tuple(records)

    def records(self) -> tuple[ResearchRecord, ...]:
        return self._records

    def get(self, abbreviation: str) -> ResearchRecord | None:
        key = abbreviation.strip().upper()
        return next((row for row in self._records if row.abbreviation == key), None)

    def backlog(self) -> Iterable[ResearchRecord]:
        return (row for row in self._records if not row.has_product_wrapper)
