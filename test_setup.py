"""
Quick setup validation script.
Tests that all modules can be imported and configuration is valid.
"""

import sys

def test_imports():
    """Test that all modules can be imported."""
    try:
        import config
        import utils
        import repost_logger
        print("All modules imported successfully")
        return True
    except ImportError as e:
        print(f"Import error: {e}")
        return False

def test_config():
    """Test configuration validation."""
    try:
        from config import Config
        Config.validate()
        print(" Configuration is valid")
        print(f"  - Monitoring user: @{Config.TIKTOK_USERNAME}")
        print(f"  - Check interval: {Config.CHECK_INTERVAL_MINUTES} minutes")
        print(f"  - Log file: {Config.LOG_FILE_PATH}")
        return True
    except ValueError as e:
        print(f"✗ Configuration error: {e}")
        return False

def test_utils():
    """Test utility functions."""
    try:
        from utils import StateManager, Logger

        # Test state manager
        state = StateManager('test_state.json')
        state.add_repost_id('test123')
        ids = state.get_seen_repost_ids()
        assert 'test123' in ids

        # Clean up
        import os
        if os.path.exists('test_state.json'):
            os.remove('test_state.json')

        print(" Utility functions working correctly")
        return True
    except Exception as e:
        print(f"✗ Utils test error: {e}")
        return False

def main():
    """Run all tests."""
    print("Running setup validation tests...\n")

    tests = [
        test_imports,
        test_config,
        test_utils,
    ]

    results = [test() for test in tests]

    print("\n" + "="*50)
    if all(results):
        print(" All tests passed! Setup is complete.")
        print("\nYou can now run the application with:")
        print("  python repost_logger.py")
        print("\nOr with Docker:")
        print("  docker-compose up -d")
        return 0
    else:
        print("✗ Some tests failed. Please fix the issues above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
