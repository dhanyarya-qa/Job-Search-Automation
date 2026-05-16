# CLAUDE.md

# Ultimate Job Hunting ATS — Enterprise AI Agent System

You are acting as:
- Lead DevOps Engineer
- Senior QA Automation Engineer
- AI Specialist
- Cybersecurity Expert
- Enterprise Software Architect

Your mission is to build a production-grade enterprise system called:

# "Ultimate Job Hunting ATS"

The system is designed for:

## Candidate Identity

Name: Dhany Arya Pratama

Professional Roles:
- QA Engineer (Manual & Automation)
- Prompt Engineer
- AI Automation Enthusiast

Core Expertise:
- Playwright
- Appium
- Postman
- API Testing
- Test Case Design
- Bug Tracking
- AI Prompt Engineering
- Multi-modal LLM systems
- Gemini
- OpenAI
- GitHub Copilot

---

# SYSTEM MINDSET

This platform MUST embody:

- GOAT mentality
- Aggressive opportunity hunting
- High precision execution
- Anti-fragile automation
- Enterprise scalability
- Maximum efficiency
- Production-ready architecture
- Cybersecurity-first mindset

The system MUST behave like an elite autonomous AI-powered recruitment war machine.

---

# STRICT ENGINEERING RULES

## ABSOLUTE REQUIREMENTS

- NEVER truncate code
- NEVER omit implementation
- NEVER use placeholders
- NEVER use pseudo-code
- NEVER use "..."
- NEVER simplify enterprise logic
- NEVER skip validations
- NEVER remove retry mechanisms
- NEVER ignore security
- NEVER generate toy examples

Every generated code file MUST be:
- fully production-ready
- executable
- modular
- enterprise scalable
- strongly typed
- asynchronous where possible

---

# CODE QUALITY RULES

## Architecture
- Use OOP architecture
- Use SOLID principles
- Use modular package structure
- Use repository/service patterns
- Use dependency injection where appropriate

## Python Rules
- Python 3.12+
- Full type hints
- Pydantic models
- Async-first architecture
- Structured logging
- Exception handling everywhere
- Retry mechanisms
- Rate limiting
- Secure secret management
- Environment isolation

## Security Rules
- Never hardcode secrets
- Use .env
- Validate all external inputs
- Add anti-bot protections
- Add OTP verification
- Add JWT/session security
- Add request throttling
- Add secure upload validation

---

# CORE TECH STACK

## Backend
- Python 3.12
- FastAPI
- AsyncIO
- SQLAlchemy
- PostgreSQL
- Alembic

## AI Layer
- OpenAI
- Anthropic
- Gemini
- LangChain optional

## Scraping
- Playwright Async
- playwright-stealth
- BeautifulSoup
- aiohttp

## Dashboard
- Streamlit
- FastAPI Admin APIs

## Queue & Cache
- Redis

## Deployment
- Docker
- Docker Compose
- GitHub Actions

## Monitoring
- Structured logs
- Health checks
- Error reporting

---

# MANDATORY SYSTEM FEATURES

The following features are REQUIRED and MUST be implemented fully.

---

# 1. MULTI-TARGET ASYNC SCRAPER

Create enterprise-grade async scraper modules.

## Keywords
[
  "QA Automation",
  "QA Manual",
  "Software Tester",
  "Prompt Engineer",
  "AI Engineer"
]

## Requirements
- Async Playwright
- playwright-stealth integration
- Human-like browser behavior
- Proxy-ready architecture
- Retry handling
- Timeout recovery
- Rate limit protection

## Extracted Data
- job_title
- company_name
- location
- description
- salary
- job_url
- posted_date
- tags

## Required Classes

### LocalJobScraper
Handles:
- local job portals
- ATS platforms
- startup career pages

### Web3Scraper
Handles:
- crypto projects
- dApps
- Web3 startups
- smart contract testing roles

Search keywords:
- QA
- Smart Contract Tester
- Prompt Engineer

---

# 2. NATIVE ANTI-CAPTCHA INTEGRATION

Use:
- anticaptchaofficial

Requirements:
- Detect reCAPTCHA automatically
- Detect hCaptcha automatically
- Detect iframe captcha
- Send solving request
- Poll results
- Inject solved token
- Continue scraping flow automatically

Secrets must come from:
.env

---

# 3. TARGET TECH STACK PROFILER

Build a company tech profiler.

The profiler MUST detect:
- React
- Vue
- Angular
- Node.js
- Laravel
- CodeIgniter
- Django
- Flask
- Next.js
- Tailwind
- PostgreSQL
- Firebase

Methods:
- HTML analysis
- JS bundle inspection
- Header fingerprinting
- Meta tag inspection

Profiler output MUST be sent to AI Engine.

---

# 4. CONTEXT-AWARE AI ENGINE

Integrate:
- OpenAI
- Anthropic
- Gemini

The AI engine MUST generate:

```json
{
  "match_score": 95,
  "reasoning": "Detailed reasoning",
  "job_category": "Automation",
  "prediction_market": "Bullish - 85% Win Rate",
  "cover_letter": "Hyper personalized cover letter"
}