"""
Configuration management for TikTok Repost Logger.
Loads settings from environment variables with sensible defaults.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration settings."""

    # TikTok settings
    TIKTOK_USERNAME = os.getenv('TIKTOK_USERNAME')
    TIKTOK_EMAIL = os.getenv('TIKTOK_EMAIL')
    TIKTOK_PASSWORD = os.getenv('TIKTOK_PASSWORD')

    # Scheduling settings
    CHECK_INTERVAL_MINUTES = int(os.getenv('CHECK_INTERVAL_MINUTES', '3'))

    # File paths
    LOG_FILE_PATH = os.getenv('LOG_FILE_PATH', 'reposts.log')
    STATE_FILE_PATH = os.getenv('STATE_FILE_PATH', 'repost_state.json')

    # Browser settings
    HEADLESS = os.getenv('HEADLESS', 'true').lower() == 'true'
    BROWSER_TYPE = os.getenv('BROWSER_TYPE', 'chromium')

    # Retry settings
    MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))
    RETRY_DELAY_SECONDS = int(os.getenv('RETRY_DELAY_SECONDS', '5'))

    # Notification settings
    ENABLE_NOTIFICATIONS = os.getenv('ENABLE_NOTIFICATIONS', 'false').lower() == 'true'

    # Email notifications
    EMAIL_NOTIFICATIONS = os.getenv('EMAIL_NOTIFICATIONS', 'false').lower() == 'true'
    SMTP_HOST = os.getenv('SMTP_HOST', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
    SMTP_USERNAME = os.getenv('SMTP_USERNAME')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
    NOTIFICATION_EMAIL = os.getenv('NOTIFICATION_EMAIL')

    # Telegram notifications
    TELEGRAM_NOTIFICATIONS = os.getenv('TELEGRAM_NOTIFICATIONS', 'false').lower() == 'true'
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

    @classmethod
    def validate(cls):
        """Validate required configuration settings."""
        if not cls.TIKTOK_USERNAME:
            raise ValueError(
                "TIKTOK_USERNAME must be set in environment variables or .env file"
            )

        if cls.CHECK_INTERVAL_MINUTES < 1:
            raise ValueError(
                "CHECK_INTERVAL_MINUTES must be at least 1 minute"
            )

        return True

    @classmethod
    def display(cls):
        """Display current configuration (hiding sensitive data)."""
        return {
            'TIKTOK_USERNAME': cls.TIKTOK_USERNAME,
            'CHECK_INTERVAL_MINUTES': cls.CHECK_INTERVAL_MINUTES,
            'LOG_FILE_PATH': cls.LOG_FILE_PATH,
            'STATE_FILE_PATH': cls.STATE_FILE_PATH,
            'HEADLESS': cls.HEADLESS,
            'BROWSER_TYPE': cls.BROWSER_TYPE,
            'MAX_RETRIES': cls.MAX_RETRIES,
            'RETRY_DELAY_SECONDS': cls.RETRY_DELAY_SECONDS,
            'TIKTOK_EMAIL': '***' if cls.TIKTOK_EMAIL else None,
            'TIKTOK_PASSWORD': '***' if cls.TIKTOK_PASSWORD else None,
        }
