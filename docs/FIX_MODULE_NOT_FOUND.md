# 🔧 Fix: ModuleNotFoundError: No module named 'bot.config'

## 🐛 Problem

```
Traceback (most recent call last):
  File "/home/jhopan/Play-Youtube-In-CLI/main.py", line 21, in <module>
    from bot.config import TOKEN, LOG_LEVEL, LOG_FORMAT, validate_config
ModuleNotFoundError: No module named 'bot.config'
```

## 🔍 Diagnosis

Jalankan diagnostic script untuk cek masalah:

```bash
cd ~/Play-Youtube-In-CLI
python scripts/diagnose.py
```

Script ini akan check:
- Struktur folder `bot/`
- Semua `__init__.py` files
- Import bot modules
- Dependencies
- Environment

## ✅ Solutions

### Solution 1: Fresh Clone (Recommended)

```bash
# Hapus folder lama
cd ~
rm -rf Play-Youtube-In-CLI

# Clone ulang
git clone https://github.com/jhopan/Play-Youtube-In-CLI.git
cd Play-Youtube-In-CLI

# Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure
cp .env.example .env
nano .env

# Run
python main.py
```

### Solution 2: Git Pull

Mungkin folder `bot/` tidak ter-clone lengkap:

```bash
cd ~/Play-Youtube-In-CLI

# Pull latest
git pull

# Check struktur
ls -la bot/
ls -la bot/core/
ls -la bot/handlers/
ls -la bot/utils/

# Reinstall
source venv/bin/activate
pip install -r requirements.txt

# Run
python main.py
```

### Solution 3: Check Folder Structure

Pastikan struktur lengkap:

```bash
cd ~/Play-Youtube-In-CLI
tree -L 2 bot/
```

Seharusnya tampak seperti ini:
```
bot/
├── __init__.py
├── config.py
├── core/
│   ├── __init__.py
│   ├── mpv_player.py
│   ├── playback.py
│   ├── player_state.py
│   └── youtube.py
├── handlers/
│   ├── __init__.py
│   ├── callbacks.py
│   ├── commands.py
│   └── messages.py
└── utils/
    ├── __init__.py
    ├── access_control.py
    ├── formatters.py
    └── keyboards.py
```

Jika ada yang missing:

```bash
# Clone ulang (Solution 1)
```

### Solution 4: Manual Check

```bash
cd ~/Play-Youtube-In-CLI

# Check apakah file ada
ls -lh bot/__init__.py
ls -lh bot/config.py
ls -lh bot/core/__init__.py
ls -lh bot/handlers/__init__.py
ls -lh bot/utils/__init__.py

# Jika ada yang not found, git pull atau clone ulang
```

### Solution 5: PYTHONPATH Fix (Temporary)

Jika semua file ada tapi masih error:

```bash
cd ~/Play-Youtube-In-CLI
source venv/bin/activate

# Add current dir to PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Run
python main.py
```

Atau edit main.py, tambah di paling atas (setelah shebang):

```python
import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent))
```

### Solution 6: Check File Permissions

```bash
cd ~/Play-Youtube-In-CLI

# Check permissions
ls -la bot/

# Make sure files readable
chmod -R 644 bot/*.py
chmod -R 644 bot/*/*.py
chmod -R 755 bot/
chmod -R 755 bot/*/
```

## 🧪 Verify Fix

Setelah apply solution, test dengan:

```bash
cd ~/Play-Youtube-In-CLI
source venv/bin/activate
python -c "from bot.config import TOKEN; print('✓ Import successful')"
```

Jika berhasil:
```
✓ Import successful
```

Sekarang run bot:
```bash
python main.py
```

## 🔄 Common Issues After Fix

### Issue 1: `.env` not found

```bash
cp .env.example .env
nano .env
# Add BOT_TOKEN
```

### Issue 2: Module telegram not found

```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Issue 3: MPV not found

```bash
sudo apt install mpv ffmpeg -y
```

## 💡 Prevention

Untuk avoid masalah ini di masa depan:

### 1. Always use virtual environment

```bash
source venv/bin/activate
```

### 2. Clone dengan depth full

```bash
git clone --depth 1 https://github.com/jhopan/Play-Youtube-In-CLI.git
```

### 3. Check setelah clone

```bash
cd Play-Youtube-In-CLI
python scripts/diagnose.py
```

## 🆘 Still Not Working?

Jika semua solution di atas tidak berhasil:

### Option A: Manual Download

1. Download ZIP dari GitHub
2. Extract ke `~/Play-Youtube-In-CLI`
3. Follow setup instructions

### Option B: Check Git Config

```bash
# Check git autocrlf (might cause issues)
git config --global core.autocrlf
# Should be: false or input

# Fix if needed
git config --global core.autocrlf input

# Clone ulang
rm -rf ~/Play-Youtube-In-CLI
git clone https://github.com/jhopan/Play-Youtube-In-CLI.git
```

### Option C: Use Backup Version

Jika modular version bermasalah, gunakan backup monolithic:

```bash
cd ~/Play-Youtube-In-CLI
source venv/bin/activate

# Run backup version
python backup/ytmusic_interactive_bot.py
```

**Note:** Backup version tidak pakai `.env`, harus edit TOKEN di file.

## 📞 Get Help

Jika masih error setelah semua solution:

1. Run diagnostic: `python scripts/diagnose.py`
2. Share output diagnostic
3. Check error message detail
4. Verify Python version: `python --version` (need 3.8+)

---

**Quick Fix Command:**
```bash
cd ~ && rm -rf Play-Youtube-In-CLI && git clone https://github.com/jhopan/Play-Youtube-In-CLI.git && cd Play-Youtube-In-CLI && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt && cp .env.example .env && echo "✅ Done! Now edit .env and run: python main.py"
```
