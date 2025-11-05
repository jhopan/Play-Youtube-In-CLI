#!/usr/bin/env python3
"""
Test script for UI enhancements
Validates new keyboard layouts and callback handlers
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_keyboards():
    """Test keyboard layouts"""
    print("🧪 Testing Keyboard Layouts...")
    
    try:
        from bot.utils.keyboards import Keyboards
        from bot.core.player_state import player
        
        # Test main menu
        print("  ✓ Main menu layout")
        main_menu = Keyboards.main_menu()
        assert main_menu is not None
        assert len(main_menu.inline_keyboard) == 6  # 6 rows
        
        # Test volume menu
        print("  ✓ Volume menu layout")
        volume_menu = Keyboards.volume_menu()
        assert volume_menu is not None
        assert len(volume_menu.inline_keyboard) == 4  # 4 rows: +/-, presets (2 rows), mute+back
        
        # Test auto-next dialog
        print("  ✓ Auto-next dialog")
        auto_next = Keyboards.auto_next_dialog()
        assert auto_next is not None
        assert len(auto_next.inline_keyboard) == 1  # 1 row: continue + stop
        
        print("✅ Keyboard layouts OK\n")
        return True
        
    except Exception as e:
        print(f"❌ Keyboard test failed: {e}\n")
        return False


def test_callbacks():
    """Test callback handlers exist"""
    print("🧪 Testing Callback Handlers...")
    
    try:
        from bot.handlers import callbacks
        
        # Check main handler exists
        print("  ✓ Main button_callback")
        assert hasattr(callbacks, 'button_callback')
        
        # Check new handlers exist
        handlers = [
            'handle_show_info',
            'handle_auto_next_continue',
            'handle_auto_next_stop',
            'handle_volume_change',
        ]
        
        for handler in handlers:
            print(f"  ✓ {handler}")
            assert hasattr(callbacks, handler)
        
        print("✅ Callback handlers OK\n")
        return True
        
    except Exception as e:
        print(f"❌ Callback test failed: {e}\n")
        return False


def test_playback():
    """Test playback manager enhancements"""
    print("🧪 Testing Playback Manager...")
    
    try:
        from bot.core.playback import PlaybackManager
        
        # Check auto-next dialog method exists
        print("  ✓ show_auto_next_dialog method")
        assert hasattr(PlaybackManager, 'show_auto_next_dialog')
        
        # Check handle_song_finished updated
        print("  ✓ handle_song_finished method")
        assert hasattr(PlaybackManager, 'handle_song_finished')
        
        print("✅ Playback manager OK\n")
        return True
        
    except Exception as e:
        print(f"❌ Playback test failed: {e}\n")
        return False


def test_volume_controls():
    """Test volume control functions"""
    print("🧪 Testing Volume Controls...")
    
    try:
        from bot.core.mpv_player import MPVPlayer
        
        # Check volume functions exist
        functions = [
            'volume_up',
            'volume_down',
            'toggle_mute',
        ]
        
        for func in functions:
            print(f"  ✓ {func}")
            assert hasattr(MPVPlayer, func)
        
        print("✅ Volume controls OK\n")
        return True
        
    except Exception as e:
        print(f"❌ Volume test failed: {e}\n")
        return False


def test_imports():
    """Test all imports work"""
    print("🧪 Testing Module Imports...")
    
    try:
        print("  ✓ bot.config")
        from bot import config
        
        print("  ✓ bot.core.player_state")
        from bot.core import player_state
        
        print("  ✓ bot.core.mpv_player")
        from bot.core import mpv_player
        
        print("  ✓ bot.core.playback")
        from bot.core import playback
        
        print("  ✓ bot.handlers.callbacks")
        from bot.handlers import callbacks
        
        print("  ✓ bot.utils.keyboards")
        from bot.utils import keyboards
        
        print("✅ All imports OK\n")
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("=" * 50)
    print("UI ENHANCEMENTS TEST SUITE")
    print("=" * 50)
    print()
    
    results = []
    
    # Run tests in order
    results.append(("Imports", test_imports()))
    results.append(("Keyboards", test_keyboards()))
    results.append(("Callbacks", test_callbacks()))
    results.append(("Playback", test_playback()))
    results.append(("Volume Controls", test_volume_controls()))
    
    # Summary
    print("=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print()
    
    # Overall result
    all_passed = all(result for _, result in results)
    if all_passed:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
