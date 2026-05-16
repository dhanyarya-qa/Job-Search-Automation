# 🚀 GitHub Setup Guide - Ultimate Job Hunting ATS

## 📋 Status
✅ Git repository telah diinisialisasi
✅ Semua file telah di-commit
✅ Branch main telah dibuat
✅ GitHub Actions workflow telah dikonfigurasi

---

## 🔧 Langkah Setup GitHub

### 1. Buat Repository Baru di GitHub

1. Buka https://github.com/new
2. Isi detail repository:
   - **Repository name:** `ultimate-job-hunting-ats` (atau nama lain yang Anda inginkan)
   - **Description:** `🎯 Enterprise AI-Powered Job Hunting ATS - Automated job scraping, AI analysis, and application tracking`
   - **Visibility:** Private (disarankan karena ada API keys)
   - **JANGAN** centang "Initialize this repository with a README"
3. Klik **Create repository**

### 2. Push ke GitHub

Setelah repository dibuat, jalankan command berikut di terminal:

```bash
# Tambahkan remote repository (ganti USERNAME dengan username GitHub Anda)
git remote add origin https://github.com/USERNAME/ultimate-job-hunting-ats.git

# Push ke GitHub
git push -u origin main
```

**Atau jika menggunakan SSH:**
```bash
git remote add origin git@github.com:USERNAME/ultimate-job-hunting-ats.git
git push -u origin main
```

---

## 🔐 Setup GitHub Secrets

Untuk GitHub Actions berjalan dengan baik, Anda perlu menambahkan secrets:

### Cara Menambahkan Secrets:
1. Buka repository di GitHub
2. Klik **Settings** → **Secrets and variables** → **Actions**
3. Klik **New repository secret**
4. Tambahkan secrets berikut:

### Required Secrets:

| Secret Name | Value | Keterangan |
|-------------|-------|------------|
| `OPENAI_API_KEY` | `sk-proj-33vOk3...` | OpenAI API key untuk GPT-4o |
| `ANTHROPIC_API_KEY` | `sk-or-v1-288812...` | Anthropic API key untuk Claude |
| `GEMINI_API_KEY` | `AIzaSyAc0lmxjf...` | Google Gemini API key |
| `TELEGRAM_BOT_TOKEN` | `8646791127:AAHdu2...` | Telegram bot token untuk notifikasi |
| `TELEGRAM_CHAT_ID` | `1927252497` | Telegram chat ID Anda |
| `SECRET_KEY` | `your-super-secret-key-min-32-chars-here` | App secret key (min 32 karakter) |
| `JWT_SECRET_KEY` | `bR7xQ2nL9vTp4Yk8...` | JWT secret key (min 32 karakter) |
| `ANTICAPTCHA_API_KEY` | `your-anticaptcha-key` | (Optional) AntiCaptcha API key |

**⚠️ PENTING:** Jangan pernah commit file `.env` ke GitHub! File ini sudah ada di `.gitignore`.

---

## ⚙️ GitHub Actions Workflow

Workflow akan berjalan otomatis:

### 🕐 Schedule (Cron)
- **Setiap jam** (`0 * * * *`) - Scrape jobs dan jalankan AI analysis

### 🔄 Trigger Manual
- Buka **Actions** tab di GitHub
- Pilih workflow **Ultimate Job Hunting ATS — Automated Pipeline**
- Klik **Run workflow**

### 📊 Workflow Steps:

1. **Code Quality** ✅
   - Lint dengan Ruff
   - Type check dengan MyPy

2. **Run Tests** ✅
   - Pytest dengan coverage
   - Upload coverage ke Codecov (optional)

3. **Scraper Job** 🤖
   - Install Playwright
   - Scrape job listings dari LinkedIn, JobStreet, Glints, Kalibrr, Web3 boards
   - Run AI engine untuk analisis
   - Generate report
   - Upload artifacts
   - Commit outputs ke repository

---

## 📁 Artifacts

Setiap workflow run akan menghasilkan artifacts yang bisa didownload:

- **Name:** `ats-outputs-{run_number}`
- **Contents:** 
  - JSON job data
  - CSV exports
  - HTML/Markdown reports
  - AI analysis results
- **Retention:** 30 hari

### Download Artifacts:
1. Buka **Actions** tab
2. Klik workflow run yang ingin dilihat
3. Scroll ke bawah ke section **Artifacts**
4. Klik nama artifact untuk download

---

## 🔍 Monitoring Workflow

### Melihat Logs:
1. Buka **Actions** tab di GitHub
2. Klik workflow run yang ingin dilihat
3. Klik job yang ingin dilihat (Quality, Test, Scrape)
4. Expand step untuk melihat detail logs

### Status Badge:
Tambahkan badge di README untuk menampilkan status workflow:

```markdown
[![CI/CD](https://github.com/USERNAME/ultimate-job-hunting-ats/actions/workflows/job_bot.yml/badge.svg)](https://github.com/USERNAME/ultimate-job-hunting-ats/actions/workflows/job_bot.yml)
```

---

## 🛠️ Troubleshooting

### Error: "Permission denied (publickey)"
**Solusi:** Setup SSH key atau gunakan HTTPS dengan Personal Access Token

```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "dhanyarya095@gmail.com"

# Add ke GitHub: Settings → SSH and GPG keys → New SSH key
```

### Error: "Repository not found"
**Solusi:** Pastikan repository sudah dibuat di GitHub dan URL remote benar

```bash
# Cek remote URL
git remote -v

# Update remote URL jika salah
git remote set-url origin https://github.com/USERNAME/ultimate-job-hunting-ats.git
```

### Workflow Gagal
**Solusi:** 
1. Cek logs di Actions tab
2. Pastikan semua secrets sudah ditambahkan
3. Pastikan API keys valid dan memiliki quota

---

## 📝 Update Workflow

Jika ingin mengubah schedule atau konfigurasi workflow:

1. Edit file `.github/workflows/job_bot.yml`
2. Commit dan push perubahan
3. Workflow akan otomatis update

### Contoh: Ubah Schedule ke Setiap 2 Jam
```yaml
on:
  schedule:
    - cron: "0 */2 * * *"  # Setiap 2 jam
```

---

## 🎯 Next Steps

Setelah push ke GitHub:

1. ✅ Verifikasi repository di GitHub
2. ✅ Tambahkan semua required secrets
3. ✅ Trigger workflow manual pertama kali untuk testing
4. ✅ Monitor logs untuk memastikan tidak ada error
5. ✅ Setup notifications (email/Slack) untuk workflow failures (optional)

---

## 📞 Support

Jika ada masalah:
- Cek GitHub Actions logs
- Review error messages
- Pastikan semua dependencies terinstall
- Verifikasi API keys dan secrets

---

*Setup guide dibuat pada: 16 Mei 2026*
*Repository: Ultimate Job Hunting ATS*
