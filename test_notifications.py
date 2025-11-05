"""
Test script for notification system.
Run this to verify your notification settings are working.
"""

from notifications import NotificationService
from config import Config

def main():
    """Test notification configuration."""
    print("=" * 60)
    print("TikTok Repost Logger - Notification Test")
    print("=" * 60)
    print()

    # Validate config
    try:
        Config.validate()
    except ValueError as e:
        print(f"Configuration error: {e}")
        return

    # Check what's enabled
    print("Configuration:")
    print(f"  Notifications enabled: {Config.ENABLE_NOTIFICATIONS}")
    print(f"  Email notifications: {Config.EMAIL_NOTIFICATIONS}")
    print(f"  Telegram notifications: {Config.TELEGRAM_NOTIFICATIONS}")
    print()

    if not Config.ENABLE_NOTIFICATIONS:
        print("⚠️  Notifications are disabled.")
        print("Set ENABLE_NOTIFICATIONS=true in your .env file")
        return

    if not Config.EMAIL_NOTIFICATIONS and not Config.TELEGRAM_NOTIFICATIONS:
        print("⚠️  No notification methods enabled.")
        print("Enable EMAIL_NOTIFICATIONS or TELEGRAM_NOTIFICATIONS in your .env file")
        return

    # Test notifications
    notifier = NotificationService()
    notifier.test_notifications()

    print()
    print("=" * 60)
    print("Test complete! Check your email/Telegram for test messages.")
    print("=" * 60)

if __name__ == '__main__':
    main()
