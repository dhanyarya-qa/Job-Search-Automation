# 📱 Telegram Channel Setup Guide

Panduan lengkap untuk menghubungkan bot ke Telegram Channel agar job postings bisa dikirim ke channel publik.

## 🎯 Fitur

- ✅ Kirim job ke personal chat (private)
- ✅ Kirim job ke channel (public/private)
- ✅ Otomatis kirim ke kedua tempat
- ✅ Support inline buttons untuk apply

---

## 📋 Prerequisites

1. Bot Telegram sudah dibuat (via @BotFather)
2. Channel Telegram sudah dibuat
3. Bot token dan chat ID sudah dikonfigurasi

---

## 🚀 Setup Steps

### Step 1: Tambahkan Bot ke Channel

1. Buka channel Telegram kamu: https://t.me/+wchyhkrRqJoyMGM9
2. Klik **Channel Info** (nama channel di atas)
3. Klik **Administrators**
4. Klik **Add Administrator**
5. Cari bot kamu: `@nyarioportunitibot`
6. Berikan permission:
   - ✅ **Post Messages** (wajib)
   - ✅ **Edit Messages** (optional)
   - ✅ **Delete Messages** (optional)
7. Klik **Save**

### Step 2: Dapatkan Channel ID

Ada 3 cara untuk mendapatkan Channel ID:

#### Cara 1: Menggunakan Script (Recommended)

```bash
python scripts/get_channel_id.py
```

Script ini akan:
- Membaca updates dari bot
- Mencari channel yang bot sudah join
- Menampilkan Channel ID

#### Cara 2: Menggunakan @userinfobot

1. Forward sebuah message dari channel ke @userinfobot
2. Bot akan reply dengan info channel termasuk ID
3. Format ID: `-100xxxxxxxxxx`

#### Cara 3: Manual via Telegram Web

1. Buka channel di Telegram Web: https://web.telegram.org
2. URL akan seperti: `https://web.telegram.org/k/#-1001234567890`
3. Angka setelah `#` adalah Channel ID

### Step 3: Update .env File

Tambahkan Channel ID ke file `.env`:

```env
# Telegram Configuration
TELEGRAM_BOT_TOKEN=7924084494:AAH...
TELEGRAM_CHAT_ID=1927252497
TELEGRAM_CHANNEL_ID=-1001234567890  # <-- Tambahkan ini
```

**Format Channel ID:**
- Harus diawali dengan `-100`
- Contoh: `-1001234567890`
- Jangan pakai quotes

### Step 4: Test Connection

Test apakah bot bisa kirim ke channel:

```bash
python scripts/test_channel.py
```

Script ini akan:
- Kirim test message ke personal chat
- Kirim test message ke channel
- Verifikasi kedua berhasil

---

## 🧪 Testing

### Test 1: Kirim Test Message

```bash
python scripts/test_channel.py
```

Expected output:
```
✅ Message sent successfully!

Check:
1. Your personal chat with bot
2. Your channel: https://t.me/+wchyhkrRqJoyMGM9
```

### Test 2: Kirim Job Posting

```bash
python scripts/run_job_finder_optimized.py
```

Job akan dikirim ke:
- ✅ Personal chat (dengan buttons)
- ✅ Channel (dengan buttons)

---

## 🔧 Troubleshooting

### Error: "Chat not found"

**Penyebab:** Bot belum ditambahkan ke channel atau Channel ID salah

**Solusi:**
1. Pastikan bot sudah jadi admin di channel
2. Cek Channel ID format: `-100xxxxxxxxxx`
3. Jalankan `python scripts/get_channel_id.py`

### Error: "Bot was kicked from the channel"

**Penyebab:** Bot di-remove dari channel

**Solusi:**
1. Tambahkan bot kembali sebagai admin
2. Berikan permission "Post Messages"

### Error: "Not enough rights to send messages"

**Penyebab:** Bot tidak punya permission untuk post

**Solusi:**
1. Buka Channel Settings → Administrators
2. Klik bot name
3. Enable "Post Messages" permission

### Message terkirim ke chat tapi tidak ke channel

**Penyebab:** Channel ID tidak dikonfigurasi atau salah

**Solusi:**
1. Cek `.env` file ada `TELEGRAM_CHANNEL_ID`
2. Pastikan format: `-100xxxxxxxxxx`
3. Restart script

---

## 📊 How It Works

### Message Flow

```
Job Found
    ↓
Filter Applied
    ↓
Send to Telegram
    ├─→ Personal Chat (TELEGRAM_CHAT_ID)
    └─→ Channel (TELEGRAM_CHANNEL_ID)
    ↓
Save to Database
```

### Code Implementation

File: `app/notifications/telegram_notifier.py`

```python
async def send_message(self, text: str, to_channel: bool = True):
    # Send to personal chat
    await bot.send_message(chat_id=self._chat_id, text=text)
    
    # Send to channel (if configured)
    if to_channel and self._channel_id:
        await bot.send_message(chat_id=self._channel_id, text=text)
```

---

## 🎨 Message Format

Job messages akan tampil seperti ini di channel:

```
🎯 New Job Found!

📋 Senior QA Engineer
🏢 Tokopedia
📍 Jakarta
💰 15-20 juta
💼 Type: Full-time
🎓 Level: Senior
🌐 Platform: LinkedIn

📨 How to Apply:
🔗 Apply Here

[📝 Apply Now] [💾 Save] [❌ Not Interested]
[🏢 Company Info]
```

---

## ⚙️ Configuration Options

### Disable Channel Posting

Jika ingin kirim hanya ke personal chat:

```python
# In code
await notifier.send_message(text, to_channel=False)
```

### Channel Only (No Personal Chat)

Edit `telegram_notifier.py`:

```python
async def send_message(self, text: str, to_channel: bool = True):
    # Skip personal chat, send to channel only
    if to_channel and self._channel_id:
        await bot.send_message(chat_id=self._channel_id, text=text)
```

---

## 📝 Notes

- Channel bisa public atau private
- Invite link format: `https://t.me/+xxxxxxxxxxx`
- Bot harus jadi admin untuk bisa post
- Messages akan muncul sebagai "Posted by [Bot Name]"
- Inline buttons akan tetap berfungsi di channel

---

## 🔗 Links

- Your Channel: https://t.me/+wchyhkrRqJoyMGM9
- Your Bot: @nyarioportunitibot
- Telegram Bot API: https://core.telegram.org/bots/api

---

## ✅ Checklist

- [ ] Bot ditambahkan ke channel sebagai admin
- [ ] Bot punya permission "Post Messages"
- [ ] Channel ID sudah didapat
- [ ] `.env` file sudah diupdate dengan `TELEGRAM_CHANNEL_ID`
- [ ] Test script berhasil: `python scripts/test_channel.py`
- [ ] Job posting terkirim ke channel

---

**Need Help?** Check the troubleshooting section or run the test scripts.
