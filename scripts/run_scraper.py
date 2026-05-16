"""
Run Scraper — Entry point script to run the full scraping pipeline.
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import structlog
from app.scraper.local_scraper import LocalJobScraper
from app.scraper.web3_scraper import Web3Scraper
from app.scraper.output_writer import OutputWriter
from app.utils.logging import configure_logging

logger = structlog.get_logger(__name__)


async def main() -> None:
    configure_logging()
    writer = OutputWriter()

    logger.info("Starting full scraping pipeline")

    # Local jobs
    local = LocalJobScraper()
    local_jobs = await local.scrape_all_keywords()
    logger.info("Local scraping done", count=len(local_jobs))

    # Web3 jobs
    web3 = Web3Scraper()
    web3_jobs = await web3.scrape_all_keywords()
    logger.info("Web3 scraping done", count=len(web3_jobs))

    all_jobs = local_jobs + web3_jobs

    writer.write_jobs_json(all_jobs, "scrape_results")
    writer.write_jobs_csv(all_jobs, "scrape_results")

    logger.info("Scraping pipeline complete", total=len(all_jobs))


if __name__ == "__main__":
    asyncio.run(main())
