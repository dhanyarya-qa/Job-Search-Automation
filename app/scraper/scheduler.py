"""
Scheduler — Async job scheduling for periodic scraping runs.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone

import structlog

logger = structlog.get_logger(__name__)


class ScraperScheduler:
    """
    Lightweight async scheduler that runs the scraper pipeline
    at configurable intervals. Used when not deploying via GitHub Actions.
    """

    def __init__(self, interval_hours: int = 1) -> None:
        self.interval_seconds = interval_hours * 3600
        self._running = False
        self._task: asyncio.Task | None = None

    async def start(self) -> None:
        """Start the scheduler loop."""
        if self._running:
            logger.warning("Scheduler already running")
            return
        self._running = True
        self._task = asyncio.create_task(self._loop())
        logger.info("Scheduler started", interval_hours=self.interval_seconds // 3600)

    async def stop(self) -> None:
        """Stop the scheduler gracefully."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Scheduler stopped")

    async def _loop(self) -> None:
        """Internal scheduler loop."""
        while self._running:
            run_start = datetime.now(tz=timezone.utc)
            logger.info("Scheduler: starting scraping run", time=run_start.isoformat())
            try:
                await self._run_pipeline()
            except Exception as e:
                logger.error("Scheduled run failed", error=str(e))

            elapsed = (datetime.now(tz=timezone.utc) - run_start).total_seconds()
            sleep_time = max(0, self.interval_seconds - elapsed)
            logger.info("Scheduler: sleeping", seconds=sleep_time)
            await asyncio.sleep(sleep_time)

    async def _run_pipeline(self) -> None:
        """Execute the full scraper + AI pipeline."""
        from app.scraper.local_scraper import LocalJobScraper  # noqa: PLC0415
        from app.scraper.web3_scraper import Web3Scraper  # noqa: PLC0415
        from app.scraper.output_writer import OutputWriter  # noqa: PLC0415

        writer = OutputWriter()

        local = LocalJobScraper()
        local_jobs = await local.scrape_all_keywords()

        web3 = Web3Scraper()
        web3_jobs = await web3.scrape_all_keywords()

        all_jobs = local_jobs + web3_jobs
        writer.write_jobs_json(all_jobs, "scheduled_scrape")
        writer.write_jobs_csv(all_jobs, "scheduled_scrape")

        logger.info("Scheduled pipeline complete", total_jobs=len(all_jobs))
