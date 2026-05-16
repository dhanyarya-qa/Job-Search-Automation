"""
AI Constants — Candidate profile data and scoring thresholds.
"""

from __future__ import annotations

# ─── Candidate Profile ───────────────────────────────────────────
CANDIDATE_NAME = "Dhany Arya Pratama"
CANDIDATE_ROLE = "QA Engineer | Prompt Engineer | AI Automation Enthusiast"

CANDIDATE_SKILLS: list[str] = [
    "Playwright",
    "Appium",
    "Postman",
    "API Testing",
    "Test Case Design",
    "Bug Tracking",
    "Selenium",
    "Python",
    "JavaScript",
    "AI Prompt Engineering",
    "Multi-modal LLM Systems",
    "Gemini",
    "OpenAI",
    "GitHub Copilot",
    "Jira",
    "CI/CD",
    "GitHub Actions",
    "REST API",
    "GraphQL",
]

CANDIDATE_EXPERIENCE_YEARS = 3
CANDIDATE_LANGUAGES = ["Indonesian", "English"]

# ─── Search Keywords ──────────────────────────────────────────────
JOB_SEARCH_KEYWORDS: list[str] = [
    "QA Automation",
    "QA Manual",
    "Software Tester",
    "Prompt Engineer",
    "AI Engineer",
    "Quality Assurance",
    "Test Engineer",
    "SDET",
]

WEB3_KEYWORDS: list[str] = [
    "QA",
    "Smart Contract Tester",
    "Prompt Engineer",
    "Web3 QA",
    "Blockchain QA",
]

# ─── Scoring Thresholds ───────────────────────────────────────────
SCORE_EXCELLENT = 90
SCORE_GOOD = 75
SCORE_AVERAGE = 60
SCORE_LOW = 40

# ─── AI Model Constants ───────────────────────────────────────────
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 2
REQUEST_TIMEOUT = 60

# ─── Prediction Market Labels ──────────────────────────────────────
PREDICTION_BULLISH = "Bullish"
PREDICTION_NEUTRAL = "Neutral"
PREDICTION_BEARISH = "Bearish"

PREDICTION_LABELS = {
    (90, 101): f"{PREDICTION_BULLISH} — 🚀 Elite Match (95%+ Win Rate)",
    (75, 90): f"{PREDICTION_BULLISH} — 💪 Strong Match (80% Win Rate)",
    (60, 75): f"{PREDICTION_NEUTRAL} — 🎯 Moderate Match (60% Win Rate)",
    (40, 60): f"{PREDICTION_BEARISH} — ⚠️  Weak Match (30% Win Rate)",
    (0, 40): f"{PREDICTION_BEARISH} — ❌ Poor Match (<20% Win Rate)",
}


def get_prediction_label(score: float) -> str:
    """Return prediction market label for a given score."""
    for (low, high), label in PREDICTION_LABELS.items():
        if low <= score < high:
            return label
    return f"{PREDICTION_BEARISH} — Unknown"
