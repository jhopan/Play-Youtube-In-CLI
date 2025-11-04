#!/usr/bin/env python3
"""
Test script for YouTube Music Bot
Run this to verify all components work
"""

import sys
import subprocess
import importlib.util

def test_python_version():
    """Test Python version"""
    print("🐍 Testing Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 7:
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"   ❌ Python {version.major}.{version.minor}.{version.micro} (need 3.7+)")
        return False

def test_package(package_name, import_name=None):
    """Test if a Python package is installed"""
    if import_name is None:
        import_name = package_name
    
    print(f"📦 Testing {package_name}...")
    spec = importlib.util.find_spec(import_name)
    if spec is not None:
        print(f"   ✅ {package_name} installed")
        return True
    else:
        print(f"   ❌ {package_name} not installed")
        print(f"      Install: pip3 install {package_name}")
        return False

def test_system_command(command, name=None):
    """Test if a system command exists"""
    if name is None:
        name = command
    
    print(f"🔧 Testing {name}...")
    try:
        result = subprocess.run(
            [command, '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            version = result.stdout.split('\n')[0]
            print(f"   ✅ {name}: {version}")
            return True
        else:
            print(f"   ❌ {name} not working")
            return False
    except FileNotFoundError:
        print(f"   ❌ {name} not installed")
        print(f"      Install: sudo apt install {command}")
        return False
    except subprocess.TimeoutExpired:
        print(f"   ❌ {name} timeout")
        return False

def test_network():
    """Test network connectivity"""
    print("🌐 Testing network...")
    try:
        result = subprocess.run(
            ['ping', '-c', '1', 'telegram.org'],
            capture_output=True,
            timeout=5
        )
        if result.returncode == 0:
            print("   ✅ Internet connection OK")
            return True
        else:
            print("   ❌ Cannot reach telegram.org")
            return False
    except Exception as e:
        print(f"   ❌ Network test failed: {e}")
        return False

def test_youtube_access():
    """Test YouTube access with yt-dlp"""
    print("🎵 Testing YouTube access...")
    try:
        result = subprocess.run(
            ['yt-dlp', '--dump-json', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'],
            capture_output=True,
            timeout=10
        )
        if result.returncode == 0:
            print("   ✅ Can access YouTube")
            return True
        else:
            print("   ❌ Cannot access YouTube")
            return False
    except FileNotFoundError:
        print("   ⚠️  yt-dlp not installed (will be tested via Python)")
        return None
    except subprocess.TimeoutExpired:
        print("   ❌ YouTube access timeout")
        return False

def test_bot_file():
    """Test if bot file exists"""
    print("📄 Testing bot file...")
    try:
        with open('ytmusic_interactive_bot.py', 'r') as f:
            content = f.read()
            
        # Check if TOKEN is configured
        if 'YOUR_BOT_TOKEN_HERE' in content:
            print("   ⚠️  Bot file exists but TOKEN not configured")
            print("      Edit ytmusic_interactive_bot.py and add your token")
            return None
        else:
            print("   ✅ Bot file exists and appears configured")
            return True
    except FileNotFoundError:
        print("   ❌ ytmusic_interactive_bot.py not found")
        return False

def test_mpv_youtube():
    """Test mpv with YouTube"""
    print("🎬 Testing mpv with YouTube...")
    try:
        process = subprocess.Popen(
            ['mpv', '--no-video', '--no-terminal', '--quiet', '--length=1',
             'https://www.youtube.com/watch?v=dQw4w9WgXcQ'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        process.wait(timeout=10)
        if process.returncode == 0:
            print("   ✅ mpv can play YouTube videos")
            return True
        else:
            print("   ⚠️  mpv test inconclusive")
            return None
    except FileNotFoundError:
        print("   ❌ mpv not found")
        return False
    except subprocess.TimeoutExpired:
        process.kill()
        print("   ✅ mpv can play YouTube (killed after timeout)")
        return True
    except Exception as e:
        print(f"   ❌ mpv test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("🧪 YouTube Music Bot - Component Test")
    print("=" * 60)
    print()
    
    results = []
    
    # Test Python version
    results.append(test_python_version())
    print()
    
    # Test Python packages
    results.append(test_package('python-telegram-bot', 'telegram'))
    results.append(test_package('yt-dlp', 'yt_dlp'))
    print()
    
    # Test system commands
    results.append(test_system_command('mpv'))
    results.append(test_system_command('ffmpeg'))
    print()
    
    # Test network
    results.append(test_network())
    print()
    
    # Test YouTube access
    yt_result = test_youtube_access()
    if yt_result is not None:
        results.append(yt_result)
    print()
    
    # Test mpv with YouTube
    mpv_result = test_mpv_youtube()
    if mpv_result is not None:
        results.append(mpv_result)
    print()
    
    # Test bot file
    bot_result = test_bot_file()
    if bot_result is not None:
        results.append(bot_result)
    print()
    
    # Summary
    print("=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    
    passed = sum(1 for r in results if r is True)
    failed = sum(1 for r in results if r is False)
    total = len(results)
    
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {failed}/{total}")
    print()
    
    if failed == 0:
        print("🎉 All tests passed! You're ready to run the bot.")
        print()
        print("Next steps:")
        print("1. Configure bot token in ytmusic_interactive_bot.py")
        print("2. Run: python3 ytmusic_interactive_bot.py")
        print("3. Send /start to your bot in Telegram")
        return 0
    else:
        print("⚠️  Some tests failed. Please fix the issues above.")
        print()
        print("Common fixes:")
        print("- Install missing packages: pip3 install python-telegram-bot yt-dlp")
        print("- Install system tools: sudo apt install mpv ffmpeg")
        print("- Check internet connection")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n❌ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        sys.exit(1)
