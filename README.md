# 🎯 Job Search Automation
### Automated Job Finder with Telegram Notifications

> **Built for:** Dhany Arya Pratama — QA Engineer | Prompt Engineer | AI Automation

[![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35-FF4B4B?logo=streamlit)](https://streamlit.io)
[![SQLite](https://img.shields.io/badge/SQLite-3-003B57?logo=sqlite)](https://sqlite.org)
[![GitHub Actions](https://img.shields.io/badge/CI%2FCD-GitHub_Actions-2088FF?logo=githubactions)](https://github.com/features/actions)

---

## 📋 Overview

Sistem otomatis untuk mencari lowongan pekerjaan dan mengirim notifikasi langsung ke Telegram. Program ini:

- 🔍 **Scrape** lowongan dari LinkedIn, JobStreet, Glints, Kalibrr setiap jam
- 📱 **Kirim** notifikasi langsung ke Telegram untuk setiap job yang ditemukan
- ✉️ **Extract** email dan link apply dari job posting
- 🔄 **Jalan otomatis** via GitHub Actions setiap 1 jam
- 💾 **Simpan** ke database untuk tracking (tidak ada duplikat)
- 📊 **Dashboard** untuk monitoring (optional)

**No AI Scoring** - Langsung kirim semua job yang ditemukan!

---

## 🚀 Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/dhanyarya-qa/Job-Search-Automation.git
cd Job-Search-Automation
```

### 2. Setup Environment

```bash
# Copy .env.example ke .env
cp .env.example .env

# Edit .env dan isi:
# - TELEGRAM_BOT_TOKEN (dari @BotFather)
# - TELEGRAM_CHAT_ID (dari @userinfobot)
```

### 3. Install Dependencies

```bash
# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Install packages
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

### 4. Setup GitHub Secrets

Buka repository di GitHub → Settings → Secrets and variables → Actions → New repository secret

Tambahkan secrets berikut:
- `TELEGRAM_BOT_TOKEN` - Token bot Telegram
- `TELEGRAM_CHAT_ID` - Chat ID Telegram kamu
- `SECRET_KEY` - Random string min 32 karakter
- `JWT_SECRET_KEY` - Random string min 32 karakter

### 5. Test Locally

```bash
# Test scraper
python scripts/test_job_finder_quick.py

# Cek Telegram, harusnya ada notifikasi job masuk!
```

---

## 📁 Project Structure

```
Job-Search-Automation/
├── app/
│   ├── scraper/                # Job scraper
│   │   ├── local_scraper.py    # LinkedIn, JobStreet, Glints, Kalibrr
│   │   ├── extractor.py        # Extract job data + email/link
│   │   ├── browser_manager.py  # Playwright browser
│   │   └── constants.py        # Keywords & platform URLs
│   │
│   ├── notifications/
│   │   └── telegram_notifier.py # Telegram bot
│   │
│   ├── database/
│   │   ├── models/             # SQLite models
│   │   │   └── job.py          # Job table
│   │   └── session.py          # Database session
│   │
│   ├── api/                    # FastAPI backend (optional)
│   │   └── endpoints/
│   │       ├── auth.py         # Login dengan OTP
│   │       └── jobs.py         # Job API
│   │
│   └── main.py                 # FastAPI app
│
├── dashboard/                  # Streamlit dashboard (optional)
│   └── app.py
│
├── scripts/
│   ├── run_job_finder_optimized.py  # Main script (dipakai GitHub Actions)
│   ├── test_job_finder_quick.py     # Test script
│   └── test_telegram.py             # Test Telegram
│
├── .github/workflows/
│   └── job_bot.yml             # Auto run setiap jam
│
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## ⚙️ Configuration

### Environment Variables (.env)

```bash
# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# Database (SQLite - otomatis dibuat)
DATABASE_URL=sqlite+aiosqlite:///./job_hunting_ats.db

# Security
SECRET_KEY=your-secret-key-min-32-chars
JWT_SECRET_KEY=your-jwt-secret-key-min-32-chars

# App
DEBUG=true
CANDIDATE_NAME="Dhany Arya Pratama"
```

### Job Keywords (app/scraper/constants.py)

```python
JOB_KEYWORDS = [
    "QA Automation",
    "QA Manual",
    "Software Tester",
    "Prompt Engineer",
    "AI Engineer",
    "Quality Assurance Engineer",
    "SDET",
    "Test Engineer",
]
```

Edit sesuai kebutuhan!

---

## 🤖 Cara Kerja

### 1. Scraping Flow

```
Start
  ↓
Scrape LinkedIn → Dapat 20 jobs
  ↓
Scrape JobStreet → Dapat 0 jobs
  ↓
Scrape Glints → Dapat 0 jobs
  ↓
Scrape Kalibrr → Dapat 0 jobs
  ↓
Total: 20 jobs
```

### 2. Notification Flow

```
Untuk setiap job:
  ↓
Cek database → Sudah pernah dikirim?
  ↓ No
Extract email & apply link dari HTML
  ↓
Format message:
  🎯 New Job Found!
  📋 [Job Title]
  🏢 [Company]
  📍 [Location]
  💰 [Salary]
  📨 How to Apply:
     ✉️ Email: [email]
     🔗 Apply: [link]
  ↓
Kirim ke Telegram
  ↓
Save ke database
```

### 3. GitHub Actions Schedule

```
Setiap jam (cron: "0 * * * *"):
  ↓
Run: python scripts/run_job_finder_optimized.py
  ↓
Scrape 3 keywords pertama
  ↓
Kirim semua jobs ke Telegram
  ↓
Done
```

---

## 📱 Setup Telegram Bot

### 1. Buat Bot

1. Chat dengan [@BotFather](https://t.me/BotFather)
2. Kirim `/newbot`
3. Ikuti instruksi
4. Copy **token** yang diberikan

### 2. Dapatkan Chat ID

1. Chat dengan [@userinfobot](https://t.me/userinfobot)
2. Bot akan kirim chat ID kamu
3. Copy **chat ID**

### 3. Test Bot

```bash
python scripts/test_telegram.py
```

Cek Telegram, harusnya ada pesan masuk!

---

## 🔄 GitHub Actions

Workflow otomatis jalan setiap jam:

### Status Workflow

Cek di: https://github.com/dhanyarya-qa/Job-Search-Automation/actions

### Manual Trigger

1. Buka Actions tab
2. Pilih "Ultimate Job Hunting ATS — Automated Pipeline"
3. Klik "Run workflow"

### Workflow Steps

```yaml
1. Code Quality (ruff + mypy)
2. Run Tests (pytest)
3. Run Job Finder:
   - Scrape jobs dari 4 platform
   - Kirim ke Telegram
   - Save ke database
4. Generate Report
5. Upload Artifacts
```

---

## 📊 Target Platforms

| Platform | Status | Jobs Found (avg) |
|----------|--------|------------------|
| LinkedIn | ✅ Working | 20+ per keyword |
| JobStreet | ✅ Working | 0-5 per keyword |
| Glints | ✅ Working | 0-5 per keyword |
| Kalibrr | ✅ Working | 0-5 per keyword |

---

## 🧪 Testing

### Test Scraper

```bash
# Test dengan 1 keyword, semua platform
python scripts/test_job_finder_quick.py
```

### Test Telegram

```bash
# Test kirim pesan ke Telegram
python scripts/test_telegram.py
```

### Test Login (Dashboard)

```bash
# Test login system
python scripts/test_login_auto.py
```

### Test All Systems

```bash
# Comprehensive test
python scripts/test_all_systems.py
```

---

## 🎯 Features

### ✅ Implemented

- [x] Scrape 4 job platforms (LinkedIn, JobStreet, Glints, Kalibrr)
- [x] Extract email & apply link dari job posting
- [x] Kirim notifikasi ke Telegram untuk setiap job
- [x] Duplicate detection (tidak kirim job yang sama 2x)
- [x] SQLite database untuk tracking
- [x] GitHub Actions auto-run setiap jam
- [x] Dashboard Streamlit (optional)
- [x] FastAPI backend dengan OTP login
- [x] Timezone-aware datetime handling

### 🚧 Future Enhancements

- [ ] Web3 job boards (CryptoJobsList, Web3.career)
- [ ] Email notifications
- [ ] Job filtering by location/salary
- [ ] Application tracking
- [ ] Cover letter generator (AI)

---

## 🛠️ Development

### Run Backend

```bash
python -m app.main
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Run Dashboard

```bash
streamlit run dashboard/app.py
# Dashboard: http://localhost:8502
```

### Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head
```

---

## 📝 Notes

- **Rate Limiting**: Scraper punya delay 1-2 detik antar request untuk avoid blocking
- **Stealth Mode**: Menggunakan random user agents dan viewport
- **Error Handling**: Semua errors di-log, workflow tetap jalan (continue-on-error)
- **Database**: SQLite untuk development, bisa ganti ke PostgreSQL untuk production

---

## 🤝 Contributing

1. Fork repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

---

## 📄 License

MIT License - Feel free to use for personal job hunting automation!

---

## 👤 Author

**Dhany Arya Pratama**
- Role: QA Engineer | Prompt Engineer | AI Automation
- Skills: Playwright, Appium, Postman, API Testing, Selenium, Python, JavaScript
- Email: dhanyarya095@gmail.com
- GitHub: [@dhanyarya-qa](https://github.com/dhanyarya-qa)

---

## 🙏 Acknowledgments

- [Playwright](https://playwright.dev/) - Browser automation
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [Streamlit](https://streamlit.io/) - Dashboard framework
- [python-telegram-bot](https://python-telegram-bot.org/) - Telegram bot library

---

**Happy Job Hunting! 🎯**
