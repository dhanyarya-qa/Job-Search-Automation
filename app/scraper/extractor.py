"""
Job Data Extractor — Extracts structured job data from pages.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone

import structlog
from bs4 import BeautifulSoup

from app.scraper.constants import TECH_FINGERPRINTS

logger = structlog.get_logger(__name__)


class JobExtractor:
    """Extracts structured job data from HTML/page content."""

    @staticmethod
    def extract_email(text: str) -> str | None:
        """Extract email address from text."""
        if not text:
            return None
        # Pattern untuk email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        match = re.search(email_pattern, text)
        if match:
            return match.group(0)
        return None

    @staticmethod
    def extract_apply_link(html_content: str, page_url: str) -> str | None:
        """Extract apply link from HTML content."""
        if not html_content:
            return None
        
        soup = BeautifulSoup(html_content, "html.parser")
        
        # Cari button/link dengan text "apply", "lamar", "submit application"
        apply_keywords = [
            "apply now", "apply", "lamar", "submit application", 
            "apply for this job", "quick apply", "easy apply"
        ]
        
        for keyword in apply_keywords:
            # Cari link dengan text yang mengandung keyword
            link = soup.find("a", string=re.compile(keyword, re.IGNORECASE))
            if link and link.get("href"):
                href = link.get("href")
                # Convert relative URL ke absolute URL
                if href.startswith("/"):
                    from urllib.parse import urlparse
                    parsed = urlparse(page_url)
                    return f"{parsed.scheme}://{parsed.netloc}{href}"
                elif href.startswith("http"):
                    return href
        
        # Fallback: cari button dengan class/id yang mengandung "apply"
        apply_button = soup.find(["a", "button"], class_=re.compile("apply", re.IGNORECASE))
        if apply_button and apply_button.get("href"):
            href = apply_button.get("href")
            if href.startswith("http"):
                return href
        
        return None

    @staticmethod
    def clean_text(text: str | None) -> str:
        if not text:
            return ""
        return re.sub(r"\s+", " ", text.strip())

    @staticmethod
    def extract_salary(text: str) -> str:
        """Extract salary information from description text."""
        if not text:
            return ""
        patterns = [
            r"(Rp[\s\d.,]+(?:juta|ribu|rb|k|M)?(?:\s*-\s*Rp[\s\d.,]+(?:juta|ribu|rb|k|M)?)?)",
            r"(\$[\d.,]+(?:\s*-\s*\$[\d.,]+)?(?:\s*(?:per\s+)?(?:month|year|annual))?)",
            r"([\d.,]+\s*(?:juta|ribu|rb|k)\s*(?:per\s+(?:bulan|tahun))?)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return ""

    @staticmethod
    def detect_tech_stack(html_content: str, description: str = "") -> list[str]:
        """Fingerprint company tech stack from HTML and description."""
        detected: list[str] = []
        combined = (html_content + description).lower()
        for tech, signals in TECH_FINGERPRINTS.items():
            for signal in signals:
                if signal.lower() in combined:
                    detected.append(tech)
                    break
        return list(set(detected))

    @staticmethod
    def extract_requirements(description: str) -> list[str]:
        """Extract bullet-point requirements from job description."""
        requirements: list[str] = []
        soup = BeautifulSoup(description, "html.parser")
        for li in soup.find_all("li"):
            text = li.get_text(strip=True)
            if text and len(text) > 10:
                requirements.append(text)
        if not requirements:
            # Fallback: split on newlines
            for line in description.split("\n"):
                cleaned = line.strip().lstrip("-•*").strip()
                if cleaned and len(cleaned) > 10:
                    requirements.append(cleaned)
        return requirements[:20]

    def build_job_dict(
        self,
        job_title: str,
        company_name: str,
        location: str,
        description: str,
        job_url: str,
        source_platform: str,
        posted_date: str = "",
        salary: str = "",
        html_content: str = "",
        apply_link: str = "",
        apply_email: str = "",
        job_type: str = "",
        experience_level: str = "",
        is_remote: bool = False,
    ) -> dict:
        """Build a complete structured job dictionary."""
        tech_stack = self.detect_tech_stack(html_content, description)
        requirements = self.extract_requirements(description)
        salary = salary or self.extract_salary(description)
        scraped_at = datetime.now(tz=timezone.utc).isoformat()
        
        # Auto-extract email dan apply link jika tidak disediakan
        if not apply_email:
            apply_email = self.extract_email(description) or self.extract_email(html_content) or ""
        
        if not apply_link and html_content:
            apply_link = self.extract_apply_link(html_content, job_url) or ""
        
        # Auto-detect job type dari title/description jika tidak disediakan
        if not job_type:
            job_type = self._detect_job_type(job_title, description)
        
        # Auto-detect experience level jika tidak disediakan
        if not experience_level:
            experience_level = self._detect_experience_level(job_title, description)
        
        # Auto-detect remote jika belum diset
        if not is_remote:
            is_remote = self._detect_remote(job_title, description, location)

        return {
            "job_title": self.clean_text(job_title),
            "company_name": self.clean_text(company_name),
            "location": self.clean_text(location),
            "salary": self.clean_text(salary),
            "description": self.clean_text(description)[:5000],
            "requirements": requirements,
            "tech_stack": tech_stack,
            "job_url": job_url.strip(),
            "apply_link": apply_link.strip() if apply_link else "",
            "apply_email": apply_email.strip() if apply_email else "",
            "posted_date": posted_date,
            "scraped_at": scraped_at,
            "source_platform": source_platform,
            "job_category_prediction": "",  # Filled by AI engine
            "job_type": job_type,
            "experience_level": experience_level,
            "is_remote": is_remote,
        }
    
    @staticmethod
    def _detect_job_type(title: str, description: str) -> str:
        """Auto-detect job type from title and description."""
        combined = (title + " " + description).lower()
        
        if any(word in combined for word in ["contract", "kontrak", "freelance", "project based"]):
            return "Contract"
        elif any(word in combined for word in ["part time", "part-time", "paruh waktu"]):
            return "Part-time"
        elif any(word in combined for word in ["internship", "intern", "magang"]):
            return "Internship"
        elif any(word in combined for word in ["full time", "full-time", "permanent", "tetap"]):
            return "Full-time"
        
        # Default
        return "Full-time"
    
    @staticmethod
    def _detect_experience_level(title: str, description: str) -> str:
        """Auto-detect experience level from title and description."""
        combined = (title + " " + description).lower()
        
        if any(word in combined for word in ["senior", "sr.", "lead", "principal", "staff"]):
            return "Senior"
        elif any(word in combined for word in ["junior", "jr.", "entry level", "fresh graduate", "freshgraduate"]):
            return "Junior"
        elif any(word in combined for word in ["mid", "middle", "intermediate", "experienced"]):
            return "Mid-level"
        
        # Default
        return "Mid-level"
    
    @staticmethod
    def _detect_remote(title: str, description: str, location: str) -> bool:
        """Auto-detect if job is remote."""
        combined = (title + " " + description + " " + location).lower()
        
        remote_keywords = [
            "remote", "work from home", "wfh", "anywhere", "distributed",
            "kerja dari rumah", "jarak jauh"
        ]
        
        return any(keyword in combined for keyword in remote_keywords)
