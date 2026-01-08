"""
Notification system for TikTok Repost Logger.
Supports email and Telegram notifications.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict
import requests

from config import Config


class NotificationService:
    """Handles sending notifications via various channels."""

    def __init__(self):
        """Initialize notification service."""
        self.email_enabled = Config.EMAIL_NOTIFICATIONS
        self.telegram_enabled = Config.TELEGRAM_NOTIFICATIONS

    def send_repost_notification(self, new_reposts: List[Dict[str, str]]):
        """
        Send notification about new reposts.

        Args:
            new_reposts: List of new repost dictionaries with 'url' and 'id'
        """
        if not Config.ENABLE_NOTIFICATIONS or not new_reposts:
            return

        # Build notification message
        count = len(new_reposts)
        title = f"🎵 {count} New TikTok Repost{'s' if count > 1 else ''} Detected!"

        # Create message body
        message_lines = [
            f"Found {count} new repost{'s' if count > 1 else ''} from @{Config.TIKTOK_USERNAME}:\n"
        ]

        for i, repost in enumerate(new_reposts, 1):
            message_lines.append(f"{i}. {repost['url']}")

        message = "\n".join(message_lines)

        # Send via configured channels
        if self.email_enabled:
            self._send_email(title, message, new_reposts)

        if self.telegram_enabled:
            self._send_telegram(title, message)

    def _send_email(self, subject: str, body: str, reposts: List[Dict[str, str]]):
        """
        Send email notification.

        Args:
            subject: Email subject
            body: Plain text body
            reposts: List of repost dictionaries
        """
        try:
            if not all([Config.SMTP_USERNAME, Config.SMTP_PASSWORD, Config.NOTIFICATION_EMAIL]):
                print("Email notifications enabled but credentials not configured")
                return

            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = Config.SMTP_USERNAME
            msg['To'] = Config.NOTIFICATION_EMAIL

            # Plain text version
            text_part = MIMEText(body, 'plain')

            # HTML version with clickable links
            html_lines = [
                "<html><body>",
                f"<h2>{subject}</h2>",
                f"<p>Found {len(reposts)} new repost{'s' if len(reposts) > 1 else ''} from @{Config.TIKTOK_USERNAME}:</p>",
                "<ol>"
            ]

            for repost in reposts:
                html_lines.append(f'<li><a href="{repost["url"]}">{repost["url"]}</a></li>')

            html_lines.extend(["</ol>", "</body></html>"])
            html_body = "\n".join(html_lines)
            html_part = MIMEText(html_body, 'html')

            # Attach parts
            msg.attach(text_part)
            msg.attach(html_part)

            # Send email
            with smtplib.SMTP(Config.SMTP_HOST, Config.SMTP_PORT) as server:
                server.starttls()
                server.login(Config.SMTP_USERNAME, Config.SMTP_PASSWORD)
                server.send_message(msg)

            print(f" Email notification sent to {Config.NOTIFICATION_EMAIL}")

        except Exception as e:
            print(f"Failed to send email notification: {e}")

    def _send_telegram(self, title: str, message: str):
        """
        Send Telegram notification.

        Args:
            title: Notification title
            message: Message body
        """
        try:
            if not all([Config.TELEGRAM_BOT_TOKEN, Config.TELEGRAM_CHAT_ID]):
                print("Telegram notifications enabled but bot token/chat ID not configured")
                return

            url = f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}/sendMessage"

            # Combine title and message
            full_message = f"<b>{title}</b>\n\n{message}"

            payload = {
                'chat_id': Config.TELEGRAM_CHAT_ID,
                'text': full_message,
                'parse_mode': 'HTML',
                'disable_web_page_preview': False
            }

            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()

            print(f" Telegram notification sent to chat {Config.TELEGRAM_CHAT_ID}")

        except Exception as e:
            print(f"Failed to send Telegram notification: {e}")

    def test_notifications(self):
        """Send test notifications to verify configuration."""
        print("\nTesting notification configuration...")

        test_reposts = [{
            'url': 'https://www.tiktok.com/@test/video/1234567890',
            'id': '1234567890'
        }]

        if self.email_enabled:
            print("Sending test email...")
            self._send_email(
                "🧪 TikTok Repost Logger - Test Notification",
                "This is a test email from TikTok Repost Logger. If you received this, email notifications are working!",
                test_reposts
            )

        if self.telegram_enabled:
            print("Sending test Telegram message...")
            self._send_telegram(
                "🧪 Test Notification",
                "This is a test message from TikTok Repost Logger. If you received this, Telegram notifications are working!"
            )

        if not self.email_enabled and not self.telegram_enabled:
            print("No notification methods enabled.")
