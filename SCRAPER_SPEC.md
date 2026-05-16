# SCRAPER_SPEC.md

# MODULE PURPOSE

Build a fully asynchronous enterprise-grade job scraping system with anti-bot resilience.

The scraper module is responsible for:
- discovering jobs
- bypassing anti-bot systems
- extracting structured job data
- profiling companies
- sending data to AI engine

---

# REQUIRED STACK

- Python 3.12+
- AsyncIO
- Playwright Async
- playwright-stealth
- aiohttp
- BeautifulSoup4
- anticaptchaofficial
- fake-useragent
- Redis
- PostgreSQL

---

# REQUIRED MODULE STRUCTURE

app/scraper/
│
├── base_scraper.py
├── local_scraper.py
├── web3_scraper.py
├── browser_manager.py
├── stealth_manager.py
├── captcha_handler.py
├── proxy_manager.py
├── rate_limiter.py
├── extractor.py
├── parser.py
├── scheduler.py
├── session_manager.py
├── output_writer.py
└── constants.py

---

# REQUIRED CLASSES

## BaseScraper

Responsibilities:
- browser initialization
- context creation
- retry handling
- error handling
- proxy injection
- captcha orchestration
- stealth activation

Methods:
- initialize_browser()
- create_context()
- scrape()
- close()
- retry_failed_request()
- save_debug_artifacts()

---

## LocalJobScraper

Responsibilities:
- scrape local portals
- scrape ATS systems
- scrape startup careers

Supported Targets:
- LinkedIn
- Kalibrr
- JobStreet
- Glints
- Greenhouse
- Lever
- custom company sites

Keywords:
- QA Automation
- QA Manual
- Software Tester
- Prompt Engineer
- AI Engineer

---

## Web3Scraper

Responsibilities:
- scrape Web3 ecosystem jobs
- scrape crypto startup jobs
- scrape dApp QA opportunities

Keywords:
- Smart Contract Tester
- QA
- Prompt Engineer

Targets:
- Crypto startup boards
- Discord-linked careers
- Remote Web3 job boards

---

# ANTI-BOT REQUIREMENTS

Mandatory:
- playwright-stealth
- rotating user agents
- viewport randomization
- randomized mouse movement
- typing delays
- retry with backoff
- proxy rotation
- cookie persistence
- session persistence

Captcha handling MUST:
- detect reCAPTCHA
- detect hCaptcha
- detect iframe captcha
- solve automatically using anticaptchaofficial

---

# CAPTCHA FLOW

1. Detect captcha iframe
2. Extract site key
3. Send request to AntiCaptcha API
4. Poll solution
5. Inject token
6. Submit verification
7. Continue workflow

---

# REQUIRED DATA OUTPUT

Every job must contain:

```json
{
  "job_title": "",
  "company_name": "",
  "location": "",
  "salary": "",
  "description": "",
  "requirements": [],
  "tech_stack": [],
  "job_url": "",
  "posted_date": "",
  "scraped_at": "",
  "source_platform": "",
  "job_category_prediction": ""
}