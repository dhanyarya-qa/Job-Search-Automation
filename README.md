# 🎯 Ultimate Job Hunting ATS
### Enterprise AI-Powered Recruitment War Machine

> **Built for:** Dhany Arya Pratama — QA Engineer | Prompt Engineer | AI Automation Enthusiast

[![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35-FF4B4B?logo=streamlit)](https://streamlit.io)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql)](https://postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)](https://docker.com)
[![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub_Actions-2088FF?logo=githubactions)](https://github.com/features/actions)

---

## 📋 System Overview

The **Ultimate Job Hunting ATS** is a production-grade, fully autonomous AI system that:

- 🤖 **Scrapes** job listings from LinkedIn, JobStreet, Glints, Kalibrr, and Web3 job boards every hour
- 🧠 **Analyzes** each job against the candidate profile using OpenAI / Anthropic / Gemini
- ✉️ **Generates** hyper-personalized cover letters and interview preparation materials
- 📊 **Visualizes** match scores, prediction markets, and application funnels on a Streamlit dashboard
- 🔔 **Alerts** via Telegram and Email for high-match opportunities
- 🔄 **Runs autonomously** via GitHub Actions CI/CD on a 1-hour cron schedule

---

## 📁 Project Structure

```
NYARI OPOR OTOMATIS/
├── app/
│   ├── ai_engine/              # Multi-provider AI orchestration
│   │   ├── orchestrator.py     # Central AI pipeline coordinator
│   │   ├── provider_manager.py # OpenAI / Anthropic / Gemini failover
│   │   ├── openai_provider.py
│   │   ├── anthropic_provider.py
│   │   ├── gemini_provider.py
│   │   ├── prompt_builder.py   # Candidate-aware prompts
│   │   ├── scoring_engine.py   # Job match scoring
│   │   ├── cover_letter_engine.py
│   │   ├── interview_engine.py
│   │   ├── portfolio_generator.py
│   │   ├── response_parser.py  # Pydantic response models
│   │   ├── retry_handler.py    # Tenacity retry decorator
│   │   └── ai_constants.py     # Candidate profile & thresholds
│   │
│   ├── scraper/                # Async enterprise scraper
│   │   ├── base_scraper.py     # Abstract base with retry/stealth
│   │   ├── local_scraper.py    # LinkedIn, JobStreet, Glints, Kalibrr
│   │   ├── web3_scraper.py     # CryptoJobsList, Web3.career, Remote3
│   │   ├── browser_manager.py  # Playwright browser lifecycle
│   │   ├── stealth_manager.py  # Anti-bot human behavior simulation
│   │   ├── captcha_handler.py  # reCAPTCHA / hCaptcha auto-solver
│   │   ├── proxy_manager.py    # Rotating proxy pool
│   │   ├── rate_limiter.py     # Token-bucket rate limiter
│   │   ├── extractor.py        # Structured job data extraction
│   │   ├── parser.py           # HTML/text parsing utilities
│   │   ├── scheduler.py        # Async periodic scheduler
│   │   ├── session_manager.py  # Cookie/session persistence
│   │   ├── tech_profiler.py    # Company tech stack fingerprinting
│   │   ├── output_writer.py    # JSON/CSV output writer
│   │   └── constants.py        # Platform URLs & keywords
│   │
│   ├── database/
│   │   ├── engine.py           # Async SQLAlchemy engine
│   │   ├── session.py          # Session dependency
│   │   ├── models/             # ORM models (9 tables)
│   │   │   ├── job.py
│   │   │   ├── company.py
│   │   │   ├── ai_analysis.py
│   │   │   ├── application.py
│   │   │   ├── followup.py
│   │   │   ├── alert.py
│   │   │   ├── otp_session.py
│   │   │   ├── generated_artifact.py
│   │   │   └── scraping_log.py
│   │   └── repositories/       # Repository pattern
│   │       ├── base_repository.py
│   │       ├── job_repository.py
│   │       ├── ai_analysis_repository.py
│   │       ├── application_repository.py
│   │       └── alert_repository.py
│   │
│   ├── api/
│   │   ├── router.py           # API route aggregator
│   │   └── endpoints/
│   │       ├── auth.py         # OTP login + JWT issuance
│   │       ├── jobs.py         # Job CRUD + search + pagination
│   │       ├── ai_analysis.py  # Trigger analysis + top matches
│   │       ├── applications.py # Application status tracking
│   │       ├── alerts.py       # Alert management
│   │       └── health.py       # Health check
│   │
│   ├── auth/
│   │   ├── jwt_handler.py      # JWT access/refresh tokens
│   │   ├── otp_handler.py      # OTP generation & verification
│   │   └── security.py         # FastAPI auth dependency
│   │
│   ├── notifications/
│   │   ├── telegram_notifier.py
│   │   └── email_notifier.py
│   │
│   ├── utils/
│   │   └── logging.py          # Structured JSON logging
│   │
│   ├── config.py               # Pydantic settings
│   ├── dependencies.py         # DI container
│   └── main.py                 # FastAPI app factory
│
├── dashboard/                  # Streamlit command center
│   ├── app.py                  # Main dashboard (home)
│   └── pages/
│       ├── 01_login.py         # OTP auth page
│       ├── 02_job_explorer.py  # Browse + search + inline AI
│       ├── 03_ai_score_dashboard.py  # Charts + top matches
│       ├── 04_alerts.py        # Alert management
│       ├── 05_cover_letter_viewer.py # Cover letter generator
│       ├── 06_followup_tracker.py    # Application pipeline
│       └── 07_interview_prep.py      # Interview Q&A generator
│
├── alembic/                    # Database migrations
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       └── 001_initial_schema.py
│
├── tests/
│   ├── conftest.py
│   ├── test_scraper/
│   │   └── test_scraper_units.py
│   ├── test_ai_engine/
│   │   ├── test_orchestrator.py
│   │   └── test_prompt_builder.py
│   ├── test_database/
│   │   └── test_job_repository.py
│   └── test_api/
│       └── test_endpoints.py
│
├── .github/workflows/
│   └── job_bot.yml             # CI/CD: lint → test → scrape → AI → commit
│
├── docker/
│   ├── Dockerfile              # FastAPI production image
│   ├── Dockerfile.dashboard    # Streamlit image
│   └── nginx.conf              # Reverse proxy + SSL
│
├── scripts/
│   ├── run_scraper.py          # Manual scraper runner
│   ├── run_ai_engine.py        # Manual AI pipeline runner
│   ├── generate_report.py      # Daily markdown report
│   └── backup_db.py            # CSV/JSON database backup
│
├── outputs/                    # Runtime artifacts (gitignored)
│   ├── json/
│   ├── csv/
│   ├── reports/
│   ├── artifacts/
│   └── debug/
│
├── docker-compose.yml
├── requirements.txt
├── pyproject.toml
├── alembic.ini
├── .env.example
└── .gitignore
```

---

## 🚀 Quick Start

### 1. Clone and Configure

```bash
git clone https://github.com/your-username/ultimate-job-hunting-ats.git
cd "ultimate-job-hunting-ats"
cp .env.example .env
# Edit .env with your API keys
```

### 2. Docker Compose (Recommended)

```bash
docker compose up -d
```

Services started:
| Service | URL |
|---------|-----|
| FastAPI Backend | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| Streamlit Dashboard | http://localhost:8501 |
| PostgreSQL | localhost:5432 |
| Redis | localhost:6379 |

### 3. Local Development

```bash
# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Run database migrations
alembic upgrade head

# Start FastAPI backend
python -m app.main

# Start Streamlit dashboard (new terminal)
streamlit run dashboard/app.py

# Run scraper manually
python scripts/run_scraper.py

# Run AI engine manually
python scripts/run_ai_engine.py
```

---

## ⚙️ Configuration

Copy `.env.example` to `.env` and configure:

| Variable | Description |
|----------|-------------|
| `GEMINI_API_KEY` | Google Gemini API key (primary AI) |
| `OPENAI_API_KEY` | OpenAI API key (fallback) |
| `ANTHROPIC_API_KEY` | Anthropic Claude key (fallback) |
| `ANTICAPTCHA_API_KEY` | AntiCaptcha.com key for CAPTCHA solving |
| `TELEGRAM_BOT_TOKEN` | Telegram bot for job alerts |
| `TELEGRAM_CHAT_ID` | Your Telegram chat ID |
| `DATABASE_URL` | PostgreSQL connection string |
| `SECRET_KEY` | App secret (min 32 chars) |

---

## 🤖 AI Engine

The AI engine uses a **provider failover chain**:

```
Primary (Gemini 2.5 Pro) → Fallback (GPT-4o) → Fallback (Claude 3.5 Sonnet)
```

For each job, the AI generates:

```json
{
  "match_score": 95,
  "reasoning": "Strong match: Playwright expertise + AI prompt skills",
  "job_category": "Automation",
  "confidence": 0.95,
  "prediction_market": "Bullish — 🚀 Elite Match (95%+ Win Rate)",
  "cover_letter": "Dear Hiring Manager...",
  "interview_questions": ["Describe your Playwright framework...", ...],
  "portfolio_suggestions": ["Build a Playwright + AI hybrid test framework", ...]
}
```

---

## 🔄 CI/CD Pipeline

GitHub Actions runs **every hour** automatically:

```
Code Quality (ruff + mypy)
    ↓
Tests (pytest + PostgreSQL + Redis)
    ↓
Scraper (LinkedIn + JobStreet + Glints + Kalibrr + Web3 boards)
    ↓
AI Engine (score + cover letter + interview prep)
    ↓
Generate Report
    ↓
Commit Outputs → Push to repo
```

### Required GitHub Secrets

```
OPENAI_API_KEY
ANTHROPIC_API_KEY
GEMINI_API_KEY
TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID
ANTICAPTCHA_API_KEY
DATABASE_URL
REDIS_URL
SECRET_KEY
JWT_SECRET_KEY
```

---

## 🛡️ Security Features

- ✅ JWT access + refresh tokens
- ✅ OTP 2FA verification (Telegram / Email)
- ✅ No hardcoded secrets — `.env` only
- ✅ Input validation on all endpoints (Pydantic)
- ✅ Rate limiting on scraper (token bucket)
- ✅ Anti-bot stealth (playwright-stealth + UA rotation)
- ✅ HTTPS-ready Nginx configuration

---

## 🧪 Running Tests

```bash
pytest tests/ -v --cov=app

# Or specific module
pytest tests/test_scraper/ -v
pytest tests/test_ai_engine/ -v
pytest tests/test_database/ -v
pytest tests/test_api/ -v
```

---

## 📊 Target Job Platforms

| Platform | Type | Region |
|----------|------|--------|
| LinkedIn | Professional | Global/Indonesia |
| JobStreet | Local | Indonesia |
| Glints | Local | Indonesia |
| Kalibrr | Local | Indonesia |
| CryptoJobsList | Web3 | Global |
| Web3.career | Web3 | Global |
| Remote3 | Web3/Remote | Global |

### Search Keywords
- QA Automation, QA Manual, Software Tester
- Prompt Engineer, AI Engineer
- SDET, Quality Assurance Engineer
- Smart Contract Tester (Web3)

---

## 👤 Candidate Profile

| Field | Value |
|-------|-------|
| Name | Dhany Arya Pratama |
| Role | QA Engineer \| Prompt Engineer \| AI Automation |
| Core Skills | Playwright, Appium, Postman, API Testing, Selenium, Python, JavaScript |
| AI Tools | OpenAI, Gemini, Anthropic, GitHub Copilot |

---

## 📄 License

MIT — Built for personal enterprise-grade job hunting automation.

---

*"The system MUST behave like an elite autonomous AI-powered recruitment war machine."*
