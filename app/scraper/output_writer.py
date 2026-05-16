"""
Output Writer — Saves scraped jobs and AI results to JSON/CSV.
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path

import structlog

from app.config import settings

logger = structlog.get_logger(__name__)


class OutputWriter:
    def __init__(self) -> None:
        self.output_dir = Path(settings.output_dir)
        self.json_dir = self.output_dir / "json"
        self.csv_dir = self.output_dir / "csv"
        self.reports_dir = self.output_dir / "reports"
        self._ensure_dirs()

    def _ensure_dirs(self) -> None:
        for d in [self.json_dir, self.csv_dir, self.reports_dir]:
            d.mkdir(parents=True, exist_ok=True)

    def _timestamp(self) -> str:
        return datetime.now(tz=timezone.utc).strftime("%Y%m%d_%H%M%S")

    def write_jobs_json(self, jobs: list[dict], label: str = "jobs") -> Path:
        filename = self.json_dir / f"{label}_{self._timestamp()}.json"
        with filename.open("w", encoding="utf-8") as f:
            json.dump(jobs, f, ensure_ascii=False, indent=2, default=str)
        logger.info("JSON written", path=str(filename), count=len(jobs))
        return filename

    def write_jobs_csv(self, jobs: list[dict], label: str = "jobs") -> Path:
        if not jobs:
            return self.csv_dir / "empty.csv"
        filename = self.csv_dir / f"{label}_{self._timestamp()}.csv"
        fieldnames = list(jobs[0].keys())
        with filename.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for job in jobs:
                writer.writerow({k: str(v) for k, v in job.items()})
        logger.info("CSV written", path=str(filename), count=len(jobs))
        return filename

    def write_report(self, content: str, label: str = "report") -> Path:
        filename = self.reports_dir / f"{label}_{self._timestamp()}.md"
        filename.write_text(content, encoding="utf-8")
        logger.info("Report written", path=str(filename))
        return filename
