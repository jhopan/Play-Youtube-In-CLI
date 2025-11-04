#!/usr/bin/env python3
"""
Diagnostic script to check module structure
Run this on your Linux server to diagnose import issues
"""

import sys
import os
from pathlib import Path

print("🔍 YouTube Music Bot - Diagnostic Tool")
print("=" * 50)
print()

# Check Python version
print(f"✓ Python Version: {sys.version}")
print(f"✓ Python Path: {sys.executable}")
print()

# Check current directory
current_dir = Path.cwd()
print(f"✓ Current Directory: {current_dir}")
print()

# Check bot folder structure
print("📁 Checking folder structure:")
print()

bot_dir = current_dir / "bot"
if bot_dir.exists():
    print(f"✓ bot/ directory exists")
    
    # Check __init__.py
    init_file = bot_dir / "__init__.py"
    if init_file.exists():
        print(f"  ✓ bot/__init__.py exists ({init_file.stat().st_size} bytes)")
    else:
        print(f"  ✗ bot/__init__.py MISSING!")
    
    # Check config.py
    config_file = bot_dir / "config.py"
    if config_file.exists():
        print(f"  ✓ bot/config.py exists ({config_file.stat().st_size} bytes)")
    else:
        print(f"  ✗ bot/config.py MISSING!")
    
    # Check subdirectories
    for subdir in ["core", "handlers", "utils"]:
        subdir_path = bot_dir / subdir
        if subdir_path.exists():
            print(f"  ✓ bot/{subdir}/ exists")
            init_subfile = subdir_path / "__init__.py"
            if init_subfile.exists():
                print(f"    ✓ bot/{subdir}/__init__.py exists")
            else:
                print(f"    ✗ bot/{subdir}/__init__.py MISSING!")
        else:
            print(f"  ✗ bot/{subdir}/ MISSING!")
else:
    print(f"✗ bot/ directory NOT FOUND!")
    print()
    print("Current directory contents:")
    for item in current_dir.iterdir():
        print(f"  - {item.name}")

print()
print("🧪 Testing imports:")
print()

# Test import bot
try:
    import bot
    print("✓ import bot - SUCCESS")
    print(f"  bot.__file__ = {bot.__file__}")
except Exception as e:
    print(f"✗ import bot - FAILED: {e}")

# Test import bot.config
try:
    from bot import config
    print("✓ from bot import config - SUCCESS")
    print(f"  config.__file__ = {config.__file__}")
except Exception as e:
    print(f"✗ from bot import config - FAILED: {e}")

# Test import specific items
try:
    from bot.config import TOKEN, LOG_LEVEL
    print("✓ from bot.config import TOKEN, LOG_LEVEL - SUCCESS")
except Exception as e:
    print(f"✗ from bot.config import TOKEN, LOG_LEVEL - FAILED: {e}")

print()
print("📦 Checking dependencies:")
print()

dependencies = [
    "telegram",
    "yt_dlp",
    "dotenv",
]

for dep in dependencies:
    try:
        __import__(dep)
        print(f"✓ {dep} - INSTALLED")
    except ImportError:
        print(f"✗ {dep} - NOT INSTALLED")

print()
print("🔧 Checking environment:")
print()

# Check .env file
env_file = current_dir / ".env"
if env_file.exists():
    print(f"✓ .env file exists ({env_file.stat().st_size} bytes)")
else:
    print(f"⚠ .env file not found")

# Check main.py
main_file = current_dir / "main.py"
if main_file.exists():
    print(f"✓ main.py exists ({main_file.stat().st_size} bytes)")
else:
    print(f"✗ main.py MISSING!")

# Check sys.path
print()
print("🛤️  Python sys.path:")
for i, path in enumerate(sys.path, 1):
    print(f"  {i}. {path}")

print()
print("=" * 50)
print("Diagnostic complete!")
print()
print("💡 If you see MISSING files, try:")
print("   git pull")
print("   ls -la bot/")
print()
print("💡 If imports fail, try:")
print("   export PYTHONPATH=$PYTHONPATH:$(pwd)")
print("   python3 main.py")
