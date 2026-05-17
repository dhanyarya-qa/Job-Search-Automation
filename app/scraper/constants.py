"""
Scraper Constants — Platform URLs, selectors, and keywords.
"""

from __future__ import annotations

# ─── Search Keywords ──────────────────────────────────────────────
JOB_KEYWORDS: list[str] = [
    "QA Automation",
    "QA Manual",
    "Software Tester",
    "Prompt Engineer",
    "AI Engineer",
    "Quality Assurance Engineer",
    "SDET",
    "Test Engineer",
]

WEB3_KEYWORDS: list[str] = [
    "QA",
    "Smart Contract Tester",
    "Prompt Engineer",
    "Web3 QA",
    "Blockchain QA",
    "dApp Tester",
]

# ─── Target Platforms ─────────────────────────────────────────────
LOCAL_PLATFORMS: dict[str, str] = {
    "linkedin": "https://www.linkedin.com/jobs/search/?keywords={keyword}&location=Indonesia",
    "jobstreet": "https://www.jobstreet.co.id/jobs/{keyword}-jobs",
    "glints": "https://glints.com/id/opportunities/jobs/explore?keyword={keyword}&country=ID",
    "kalibrr": "https://www.kalibrr.id/jobs#?keyword={keyword}",
    "indeed": "https://id.indeed.com/jobs?q={keyword}&l=Indonesia",
    "karir": "https://www.karir.com/search?q={keyword}",
    "urbanhire": "https://www.urbanhire.com/jobs?q={keyword}",
}

WEB3_PLATFORMS: dict[str, str] = {
    "cryptojobslist": "https://cryptojobslist.com/qa?q={keyword}",
    "web3career": "https://web3.career/{keyword}-jobs",
    "remote3": "https://remote3.co/{keyword}-web3-jobs",
    "techinasia": "https://www.techinasia.com/jobs/search?query={keyword}",
    "angellist": "https://angel.co/jobs?q={keyword}",
}

# ─── Browser Config ───────────────────────────────────────────────
DEFAULT_VIEWPORT = {"width": 1366, "height": 768}
VIEWPORT_VARIANTS = [
    {"width": 1366, "height": 768},
    {"width": 1440, "height": 900},
    {"width": 1920, "height": 1080},
    {"width": 1280, "height": 800},
]

DEFAULT_LOCALE = "en-US"
DEFAULT_TIMEZONE = "Asia/Jakarta"

HUMAN_TYPING_DELAY_MIN = 50   # ms
HUMAN_TYPING_DELAY_MAX = 150  # ms
HUMAN_MOUSE_MOVE_STEPS = 10

# ─── Rate Limiting ────────────────────────────────────────────────
DEFAULT_PAGE_DELAY_MIN = 2.0   # seconds
DEFAULT_PAGE_DELAY_MAX = 5.0   # seconds
BURST_LIMIT = 10
BURST_WINDOW = 60  # seconds

# ─── Tech Stack Detection ─────────────────────────────────────────
TECH_FINGERPRINTS: dict[str, list[str]] = {
    "React": ["react", "_next", "react-dom", "__REACT"],
    "Vue": ["vue.js", "nuxt", "__vue_router__"],
    "Angular": ["ng-version", "angular", "zone.js"],
    "Next.js": ["_next/static", "__NEXT_DATA__"],
    "Tailwind": ["tailwind", "tw-"],
    "Laravel": ["laravel", "csrf-token"],
    "Django": ["csrfmiddlewaretoken", "django"],
    "Flask": ["flask", "werkzeug"],
    "Node.js": ["x-powered-by: Express", "express"],
    "Firebase": ["firebase", "firebaseapp.com"],
    "PostgreSQL": ["postgresql", "postgres"],
}
