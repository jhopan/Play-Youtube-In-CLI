# 🐍 Fix: Python 3.13 Compatibility Issue

## 🐛 Error

```
AttributeError: 'Updater' object has no attribute '_Updater__polling_cleanup_cb' and no __dict__ for setting new attributes
```

## 🔍 Root Cause

Python 3.13 mengubah cara kerja object attributes, sehingga `python-telegram-bot` versi lama (20.x) tidak compatible.

## ✅ Solutions

### Solution 1: Use Python 3.11 or 3.12 (Recommended)

**Check Python version:**

```bash
python3 --version
```

**If you have Python 3.13, install Python 3.12:**

#### On Debian/Ubuntu:

```bash
# Add deadsnakes PPA (if not already added)
sudo apt update
sudo apt install software-properties-common -y
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update

# Install Python 3.12
sudo apt install python3.12 python3.12-venv python3.12-dev -y

# Recreate venv with Python 3.12
cd ~/Play-Youtube-In-CLI
rm -rf venv
python3.12 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Configure and run
cp .env.example .env
nano .env
python main.py
```

### Solution 2: Update to Latest python-telegram-bot

Update requirements.txt sudah dilakukan, pull latest:

```bash
cd ~/Play-Youtube-In-CLI
git pull

# Reinstall with updated versions
source venv/bin/activate
pip install --upgrade -r requirements.txt

# Run
python main.py
```

### Solution 3: Use pyenv (Most Flexible)

Install and manage multiple Python versions:

```bash
# Install pyenv
curl https://pyenv.run | bash

# Add to ~/.bashrc
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc

# Reload
source ~/.bashrc

# Install Python 3.12
pyenv install 3.12.0

# Set for project
cd ~/Play-Youtube-In-CLI
pyenv local 3.12.0

# Recreate venv
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

## 🚀 Quick Fix Command

### Option A: With Python 3.12

```bash
cd ~/Play-Youtube-In-CLI && \
sudo apt install python3.12 python3.12-venv -y && \
rm -rf venv && \
python3.12 -m venv venv && \
source venv/bin/activate && \
pip install --upgrade pip && \
pip install -r requirements.txt && \
echo "✅ Setup complete! Edit .env and run: python main.py"
```

### Option B: Try Updated Library

```bash
cd ~/Play-Youtube-In-CLI && \
git pull && \
source venv/bin/activate && \
pip install --upgrade -r requirements.txt && \
python main.py
```

## 📋 Version Compatibility Matrix

| Python Version | python-telegram-bot | Status          |
| -------------- | ------------------- | --------------- |
| 3.8 - 3.10     | 20.7                | ✅ Works        |
| 3.11           | 20.7                | ✅ Works        |
| 3.12           | 20.7 - 21.x         | ✅ Works        |
| 3.13           | 21.x+               | ⚠️ Experimental |

## 🔍 Verify Your Setup

```bash
# Check Python version
python --version

# Check installed package version
pip show python-telegram-bot

# Should show version 21.x or higher for Python 3.13
```

## ⚠️ Important Notes

1. **Python 3.13 is very new** (released Oct 2024) - many libraries belum fully compatible
2. **Recommended: Use Python 3.12** untuk production
3. **If you must use Python 3.13**: Update semua libraries ke latest version

## 🧪 Test After Fix

```bash
cd ~/Play-Youtube-In-CLI
source venv/bin/activate
python -c "from telegram.ext import Application; print('✅ Import successful')"
python main.py
```

## 💡 Alternative: Use Docker

Jika masih bermasalah, gunakan Docker dengan Python version yang fixed:

```bash
# Create Dockerfile
cat > Dockerfile << 'EOF'
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y mpv ffmpeg git && \
    apt-get clean

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
EOF

# Build and run
docker build -t ytmusic-bot .
docker run -d --name ytmusic-bot --restart unless-stopped ytmusic-bot
```

## 🆘 Still Having Issues?

### Check Library Versions:

```bash
pip list | grep telegram
pip list | grep yt-dlp
```

### Force Reinstall:

```bash
pip uninstall python-telegram-bot -y
pip install python-telegram-bot>=21.0
```

### Use System Python (if 3.12):

```bash
# Check system Python
python3 --version

# If 3.12 or 3.11, use it directly
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 📚 References

- [python-telegram-bot Python 3.13 support](https://github.com/python-telegram-bot/python-telegram-bot/issues/4200)
- [Python 3.13 Release Notes](https://docs.python.org/3.13/whatsnew/3.13.html)

---

**Recommendation:** Use Python 3.12 for best compatibility! 🐍
