# 🔐 Environment Configuration Guide

Panduan setup environment variables untuk YouTube Music Bot.

## 📋 Quick Setup

### 1. Copy Template

```bash
cp .env.example .env
```

### 2. Edit File `.env`

```bash
nano .env
# atau
vim .env
```

### 3. Isi Konfigurasi

```env
# Telegram Bot Configuration
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
ALLOWED_USER_IDS=123456789,987654321
DEFAULT_VOLUME=75
DEBUG=false
```

## 🔑 Konfigurasi Variabel

### `BOT_TOKEN` (Required)

Token bot Telegram dari @BotFather.

**Cara mendapatkan:**

1. Buka Telegram dan cari `@BotFather`
2. Kirim `/newbot`
3. Ikuti instruksi untuk membuat bot
4. Copy token yang diberikan

**Contoh:**

```env
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz-123456
```

### `ALLOWED_USER_IDS` (Optional)

List User ID yang boleh menggunakan bot (dipisah koma).

**Cara mendapatkan User ID:**

1. Buka Telegram dan cari `@userinfobot`
2. Kirim `/start`
3. Bot akan memberikan User ID Anda

**Penggunaan:**

- **Kosong** = Semua user bisa pakai bot
- **Ada ID** = Hanya user dengan ID tersebut yang bisa pakai

**Contoh:**

```env
# Allow specific users
ALLOWED_USER_IDS=123456789,987654321,555666777

# Allow all users (kosongkan)
ALLOWED_USER_IDS=
```

### `DEFAULT_VOLUME` (Optional)

Volume default saat bot mulai (25, 50, 75, atau 100).

**Default:** `75`

**Contoh:**

```env
DEFAULT_VOLUME=75
```

### `DEBUG` (Optional)

Enable debug logging untuk troubleshooting.

**Default:** `false`

**Contoh:**

```env
# Enable debug mode
DEBUG=true

# Normal mode
DEBUG=false
```

## 📝 Contoh Konfigurasi Lengkap

### Single User (Private Bot)

```env
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
ALLOWED_USER_IDS=123456789
DEFAULT_VOLUME=75
DEBUG=false
```

### Multiple Users (Group Bot)

```env
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
ALLOWED_USER_IDS=123456789,987654321,555666777
DEFAULT_VOLUME=50
DEBUG=false
```

### Public Bot (Everyone)

```env
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
ALLOWED_USER_IDS=
DEFAULT_VOLUME=75
DEBUG=false
```

### Development Mode

```env
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
ALLOWED_USER_IDS=123456789
DEFAULT_VOLUME=50
DEBUG=true
```

## 🔒 Security Best Practices

### ✅ DO:

- ✅ Simpan `.env` di `.gitignore`
- ✅ Jangan share file `.env`
- ✅ Gunakan `.env.example` sebagai template
- ✅ Batasi akses dengan `ALLOWED_USER_IDS`
- ✅ Regenerate token jika bocor

### ❌ DON'T:

- ❌ Commit `.env` ke Git
- ❌ Share token di public
- ❌ Hardcode token di code
- ❌ Upload `.env` ke server public

## 🚀 Testing Configuration

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Verify Configuration

```bash
python -c "from bot.config import TOKEN, ALLOWED_USERS; print(f'Token: {TOKEN[:10]}...'); print(f'Allowed Users: {ALLOWED_USERS}')"
```

### 3. Run Bot

```bash
python main.py
```

## ❗ Troubleshooting

### Token Invalid

```
Error: The token is invalid
```

**Solusi:** Periksa token di `.env`, pastikan tidak ada spasi atau karakter tambahan.

### User ID Not Working

```
⛔ Access denied
```

**Solusi:**

1. Pastikan User ID benar (angka, bukan username)
2. Periksa format: `123456789,987654321` (koma tanpa spasi)
3. Restart bot setelah update `.env`

### Module Not Found: dotenv

```
ModuleNotFoundError: No module named 'dotenv'
```

**Solusi:**

```bash
pip install python-dotenv
```

### Environment Variables Not Loaded

```
Token is empty or invalid
```

**Solusi:**

1. Pastikan file `.env` ada di root project
2. Periksa nama variabel: `BOT_TOKEN` bukan `TELEGRAM_BOT_TOKEN`
3. Restart Python/bot setelah edit `.env`

## 📁 File Structure

```
Project Root/
├── .env                  # Your actual config (DO NOT COMMIT)
├── .env.example          # Template (safe to commit)
├── .gitignore            # Contains .env
├── main.py
├── requirements.txt      # Includes python-dotenv
└── bot/
    └── config.py         # Reads from .env
```

## 🔄 Migration from Old Config

Jika sebelumnya hardcode di `config.py`:

### Old Way (config.py):

```python
TOKEN = "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
ALLOWED_USERS = [123456789, 987654321]
```

### New Way (.env):

```env
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
ALLOWED_USER_IDS=123456789,987654321
```

**Keuntungan:**

- ✅ Tidak perlu edit code
- ✅ Aman dari Git commits
- ✅ Mudah deploy ke berbagai environment
- ✅ Best practice security

## 📚 Related Documentation

- [INSTALLATION.md](INSTALLATION.md) - Setup guide
- [CONFIGURATION.md](CONFIGURATION.md) - Advanced config
- [QUICKSTART.md](QUICKSTART.md) - Quick start guide
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues

## 🆘 Need Help?

Jika masih ada masalah:

1. Periksa log bot: `journalctl -u ytmusic-bot -f`
2. Enable debug mode: `DEBUG=true`
3. Lihat [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

**Security Note:** Jangan pernah commit file `.env` ke repository!
