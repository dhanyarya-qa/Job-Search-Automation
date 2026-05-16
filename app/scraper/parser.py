"""
Parser — HTML/text parsing utilities for raw job data.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Optional

import structlog
from bs4 import BeautifulSoup

logger = structlog.get_logger(__name__)


class JobParser:
    """
    Parses raw HTML and text into structured job data.
    Used as a helper by platform-specific scrapers.
    """

    @staticmethod
    def parse_posted_date(raw_date: str) -> str:
        """
        Attempt to parse relative or absolute posted dates.
        Returns ISO string or empty string.
        """
        if not raw_date:
            return ""
        raw = raw_date.strip().lower()

        # Relative: "2 days ago", "1 week ago", etc.
        now = datetime.now(tz=timezone.utc)
        relative_patterns = [
            (r"(\d+)\s*day", lambda m: now.replace(day=now.day - int(m.group(1)))),
            (r"(\d+)\s*hour", lambda m: now),
            (r"(\d+)\s*week", lambda m: now),
            (r"just now|today", lambda m: now),
        ]
        for pattern, _ in relative_patterns:
            if re.search(pattern, raw):
                return now.isoformat()

        # Try standard date formats
        date_formats = ["%Y-%m-%d", "%d/%m/%Y", "%B %d, %Y", "%b %d, %Y"]
        for fmt in date_formats:
            try:
                dt = datetime.strptime(raw_date.strip(), fmt)
                return dt.replace(tzinfo=timezone.utc).isoformat()
            except ValueError:
                continue

        return raw_date  # Return as-is if can't parse

    @staticmethod
    def strip_html(html: str) -> str:
        """Remove HTML tags and normalize whitespace."""
        if not html:
            return ""
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text(separator=" ")
        return re.sub(r"\s+", " ", text).strip()

    @staticmethod
    def extract_tags(text: str) -> list[str]:
        """
        Extract likely tech/skill tags from job description.
        Scans for known technology keywords.
        """
        known_tags = [
            "Python", "JavaScript", "TypeScript", "React", "Vue", "Angular",
            "Node.js", "Django", "FastAPI", "Flask", "Laravel", "PHP",
            "PostgreSQL", "MySQL", "MongoDB", "Redis", "Docker", "Kubernetes",
            "CI/CD", "GitHub Actions", "Jenkins", "Playwright", "Selenium",
            "Appium", "Cypress", "Jest", "Pytest", "Postman", "REST API",
            "GraphQL", "AWS", "GCP", "Azure", "Terraform", "Linux",
            "OpenAI", "LangChain", "Gemini", "Anthropic",
        ]
        found = []
        text_lower = text.lower()
        for tag in known_tags:
            if tag.lower() in text_lower:
                found.append(tag)
        return found

    @staticmethod
    def normalize_location(location: str) -> str:
        """Normalize location string."""
        if not location:
            return ""
        location = location.strip()
        # Common normalizations
        replacements = {
            "Jakarta Selatan": "South Jakarta",
            "Jakarta Pusat": "Central Jakarta",
            "Jakarta Barat": "West Jakarta",
            "Jakarta Utara": "North Jakarta",
            "Jakarta Timur": "East Jakarta",
            "DKI Jakarta": "Jakarta",
            "Remote/WFH": "Remote",
            "WFH": "Remote",
        }
        for original, normalized in replacements.items():
            if original.lower() in location.lower():
                return normalized
        return location
