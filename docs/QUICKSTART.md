# 🎯 Quick Start Guide

Panduan cepat untuk menjalankan bot dalam 5 menit!

## 🚀 Langkah Cepat (Ubuntu Server)

### 1️⃣ Persiapan Awal (2 menit)

```bash
# Login ke Ubuntu Server via SSH
ssh user@your-server-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3 python3-pip mpv ffmpeg
```

### 2️⃣ Setup Bot (1 menit)

```bash
# Buat folder
mkdir ~/ytmusic-bot && cd ~/ytmusic-bot

# Upload file ytmusic_interactive_bot.py ke folder ini
# Bisa pakai scp, sftp, atau copy-paste

# Install Python packages
pip3 install python-telegram-bot yt-dlp
```

### 3️⃣ Konfigurasi (1 menit)

```bash
# Edit bot
nano ytmusic_interactive_bot.py
```

**Ganti baris ini:**

```python
TOKEN = "YOUR_BOT_TOKEN_HERE"
```

**Dengan token Anda (dari @BotFather):**

```python
TOKEN = "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
```

**Simpan:** `Ctrl+O` → `Enter` → `Ctrl+X`

### 4️⃣ Jalankan Bot (1 menit)

```bash
# Test run
python3 ytmusic_interactive_bot.py
```

**Anda akan lihat:**

```
2024-01-01 12:00:00 - INFO - Starting YouTube Music Player Bot...
2024-01-01 12:00:00 - INFO - Bot is running...
```

### 5️⃣ Test di Telegram (30 detik)

1. Buka bot Anda di Telegram
2. Kirim: `/start`
3. Klik: **🎶 Load Playlist**
4. Kirim link playlist YouTube
5. 🎵 **Musik akan langsung diputar!**

---

## 🎮 Cara Pakai

### Load Musik

```
/start
→ Klik [🎶 Load Playlist]
→ Kirim: https://www.youtube.com/playlist?list=...
→ ✅ Otomatis diputar!
```

### Kontrol Playback

```
▶️ Play   - Mulai/resume
⏸ Pause  - Jeda
⏭ Next   - Lagu berikutnya
⏮ Prev   - Lagu sebelumnya
⏹ Stop   - Hentikan
```

### Mode Khusus

```
🔁 Loop    - Ulangi 1 lagu (toggle: 🔁 ↔️ 🔂)
🔀 Shuffle - Acak playlist (toggle: 🔀 ↔️ 🎲)
```

### Volume

```
Klik [🔊 Volume]
→ Pilih: [25%] [50%] [75%] [100%]
```

### Lihat Queue

```
Klik [📜 Queue]
→ Lihat 10 lagu teratas
```

---

## 🔧 Setup 24/7 (Optional)

Jika ingin bot jalan terus:

### Cara 1: Screen (Simple)

```bash
# Install screen
sudo apt install screen -y

# Jalankan di screen
screen -S ytmusic
python3 ytmusic_interactive_bot.py

# Detach: Ctrl+A lalu D
# Reattach: screen -r ytmusic
```

### Cara 2: Systemd (Recommended)

```bash
# Gunakan script yang sudah disediakan
chmod +x setup_service.sh
./setup_service.sh

# Bot otomatis jalan saat server booting!
```

---

## ❓ Troubleshooting Cepat

### Bot tidak merespon

```bash
# Cek apakah jalan
ps aux | grep python3

# Restart
# Tekan Ctrl+C, lalu run lagi
python3 ytmusic_interactive_bot.py
```

### Error "Token invalid"

- Pastikan token benar dari @BotFather
- Format: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`
- Tidak ada spasi atau enter

### Error "mpv not found"

```bash
sudo apt install mpv -y
```

### Error "yt-dlp error"

```bash
pip3 install --upgrade yt-dlp
```

### Musik tidak terdengar

⚠️ **NORMAL!** Bot headless tidak output audio ke speaker.
Bot hanya menjalankan mpv di server (untuk monitoring/logging).
Anda kontrol via Telegram, tapi audio tidak ke Telegram/speaker.

---

## 📋 Checklist Setup

- [ ] Python 3 installed
- [ ] mpv installed
- [ ] ffmpeg installed
- [ ] pip packages installed
- [ ] Token configured
- [ ] Bot responds to `/start`
- [ ] Can load playlist
- [ ] Music plays (check logs)
- [ ] Buttons work

---

## 🎉 Selesai!

Bot Anda sekarang sudah jalan!

**Coba playlist:**

- Spotify Wrapped: [Cari di YouTube]
- Lagu Indonesia: [Playlist populer]
- Lo-fi Study: [Cari "lofi hip hop"]

**Nikmati! 🎵🎧**

---

## 📚 Dokumentasi Lengkap

Untuk setup advanced, baca:

- `INSTALLATION.md` - Instalasi detail
- `README.md` - Dokumentasi lengkap
- `healthcheck.sh` - Cek status bot

---

**Need help?** Check the logs:

```bash
# Jika pakai systemd
sudo journalctl -u ytmusic-bot -f

# Jika manual run
# Lihat output di terminal
```
