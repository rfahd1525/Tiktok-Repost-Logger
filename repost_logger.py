"""
TikTok Repost Logger - Main application logic.
Monitors a TikTok user's reposts and logs new ones.
"""

import asyncio
import signal
import sys
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from playwright.async_api import async_playwright, Browser, Page, TimeoutError as PlaywrightTimeout

from config import Config
from utils import StateManager, Logger, extract_video_id_from_url
from notifications import NotificationService


class TikTokRepostLogger:
    """Main class for monitoring TikTok reposts."""

    def __init__(self):
        """Initialize the TikTok Repost Logger."""
        # Validate configuration
        Config.validate()

        # Initialize state manager and logger
        self.state_manager = StateManager(Config.STATE_FILE_PATH)
        self.logger = Logger(Config.LOG_FILE_PATH)
        self.notifications = NotificationService()

        # Playwright instances
        self.browser: Optional[Browser] = None
        self.context = None
        self.page: Optional[Page] = None
        self.playwright = None

        # Running state
        self.is_running = False
        self.check_count = 0
        self.start_time = datetime.now()  # Track when container started
        self.restart_hours = 6  # Restart container every N hours to prevent corruption
        self.consecutive_failures = 0  # Track consecutive failures

        # Display configuration
        print("TikTok Repost Logger initialized with configuration:")
        for key, value in Config.display().items():
            print(f"  {key}: {value}")
        print()

    async def initialize_browser(self):
        """Initialize Playwright browser with stealth settings."""
        try:
            self.playwright = await async_playwright().start()

            # Launch browser based on config
            if Config.BROWSER_TYPE == 'firefox':
                self.browser = await self.playwright.firefox.launch(
                    headless=Config.HEADLESS
                )
            elif Config.BROWSER_TYPE == 'webkit':
                self.browser = await self.playwright.webkit.launch(
                    headless=Config.HEADLESS
                )
            else:  # Default to chromium
                self.browser = await self.playwright.chromium.launch(
                    headless=Config.HEADLESS
                )

            # Create browser context with simple settings
            self.context = await self.browser.new_context()

            # Create a new page
            self.page = await self.context.new_page()

            print("Browser initialized successfully")
            self.logger.log_info("Browser initialized successfully")

        except Exception as e:
            error_msg = f"Failed to initialize browser: {e}"
            print(f"Error: {error_msg}")
            self.logger.log_error(error_msg)
            raise

    async def login(self):
        """
        Perform TikTok login if credentials are provided.

        Note: Login may require manual intervention for CAPTCHA.
        """
        if not Config.TIKTOK_EMAIL or not Config.TIKTOK_PASSWORD:
            print("No login credentials provided, skipping login")
            return

        try:
            print("Attempting to log in to TikTok...")
            await self.page.goto('https://www.tiktok.com/login/phone-or-email/email')
            await self.page.wait_for_load_state('networkidle')

            # Wait for login form
            await self.page.wait_for_selector('input[type="text"]', timeout=10000)

            # Fill in credentials
            await self.page.fill('input[type="text"]', Config.TIKTOK_EMAIL)
            await self.page.fill('input[type="password"]', Config.TIKTOK_PASSWORD)

            # Click login button
            await self.page.click('button[type="submit"]')

            # Wait for potential CAPTCHA or successful login
            print("Login submitted. If CAPTCHA appears, please solve it manually.")
            print("Waiting 30 seconds for login to complete...")
            await asyncio.sleep(30)

            self.logger.log_info("Login completed")

        except Exception as e:
            error_msg = f"Login failed: {e}"
            print(f"Warning: {error_msg}")
            self.logger.log_error(error_msg)
            print("Continuing without login - some reposts may not be visible")

    async def fetch_reposts(self) -> List[Dict[str, str]]:
        """
        Fetch current reposts from the user's profile.

        Returns:
            List of dictionaries containing repost information
        """
        reposts = []

        try:
            # Navigate to user's profile
            profile_url = f"https://www.tiktok.com/@{Config.TIKTOK_USERNAME}"
            print(f"Fetching reposts from: {profile_url}")

            await self.page.goto(profile_url, timeout=30000, wait_until='domcontentloaded')

            # Wait for page to be interactive and content to load
            await asyncio.sleep(5)

            # Look for the "Reposts" tab - TikTok's structure may vary
            # Common selectors for the reposts tab
            repost_tab_selectors = [
                'div[data-e2e="user-post-item-list"] >> text="Reposts"',
                'div[role="tab"] >> text="Reposts"',
                '[data-e2e="repost-tab"]',
                'a:has-text("Reposts")',
            ]

            repost_tab_found = False
            for selector in repost_tab_selectors:
                try:
                    repost_tab = await self.page.wait_for_selector(selector, timeout=5000)
                    if repost_tab:
                        await repost_tab.click()
                        repost_tab_found = True
                        print("Clicked on Reposts tab")
                        await asyncio.sleep(2)
                        break
                except PlaywrightTimeout:
                    continue

            if not repost_tab_found:
                error_msg = "Could not find Reposts tab. Profile may have no reposts or TikTok structure changed."
                print(f"Warning: {error_msg}")
                self.logger.log_error(error_msg)
                # Raise exception so it can be retried if needed
                raise Exception(error_msg)

            # Wait for repost content to load
            await asyncio.sleep(3)

            # Extract all links that contain /video/ or /photo/ in the href
            # This approach gets both video and photo reposts in one query
            print("Extracting repost links...")
            try:
                all_links = await self.page.query_selector_all('a')
                for link in all_links:
                    href = await link.get_attribute('href')
                    # Accept both video and photo posts
                    if href and ('/video/' in href or '/photo/' in href):
                        # Make sure it's a full URL
                        if not href.startswith('http'):
                            href = f"https://www.tiktok.com{href}"

                        content_id = extract_video_id_from_url(href)
                        reposts.append({
                            'url': href,
                            'id': content_id
                        })
            except Exception as e:
                print(f"Error extracting links: {e}")
                self.logger.log_error(f"Error extracting links: {e}")

            # Remove duplicates
            seen_ids = set()
            unique_reposts = []
            for repost in reposts:
                if repost['id'] not in seen_ids:
                    seen_ids.add(repost['id'])
                    unique_reposts.append(repost)

            print(f"Found {len(unique_reposts)} repost(s)")
            return unique_reposts

        except PlaywrightTimeout as e:
            error_msg = f"Timeout while fetching reposts: {e}"
            print(f"Error: {error_msg}")
            self.logger.log_error(error_msg)
            return reposts

        except Exception as e:
            error_msg = f"Error fetching reposts: {e}"
            print(f"Error: {error_msg}")
            self.logger.log_error(error_msg)
            return reposts

    async def detect_and_log_new_reposts(self, current_reposts: List[Dict[str, str]]):
        """
        Compare current reposts with known reposts and log new ones.

        Args:
            current_reposts: List of current repost dictionaries
        """
        seen_ids = self.state_manager.get_seen_repost_ids()

        new_reposts = [
            repost for repost in current_reposts
            if repost['id'] not in seen_ids
        ]

        if new_reposts:
            print(f"\nFound {len(new_reposts)} new repost(s)!")
            for repost in new_reposts:
                self.logger.log_repost(repost['url'], repost['id'])
                self.state_manager.add_repost_id(repost['id'])

            # Send notifications
            if Config.ENABLE_NOTIFICATIONS:
                print("Sending notifications...")
                self.notifications.send_repost_notification(new_reposts)
        else:
            print("No new reposts detected")

        # Update last check timestamp
        self.state_manager.update_last_check()

    async def check_for_new_reposts(self):
        """Main check cycle - fetch and compare reposts."""
        retry_count = 0
        max_retries = Config.MAX_RETRIES

        while retry_count < max_retries:
            try:
                # Check if container needs periodic restart to prevent corruption
                time_running = datetime.now() - self.start_time
                if time_running > timedelta(hours=self.restart_hours):
                    hours_running = time_running.total_seconds() / 3600
                    print(f"\nContainer has been running for {hours_running:.1f} hours")
                    print("Performing preventive container restart to avoid connection issues...")
                    self.logger.log_info("Triggering preventive container restart")
                    await self.cleanup()
                    print("Exiting for container restart...")
                    sys.exit(0)  # Docker will restart the container

                # Fetch current reposts
                current_reposts = await self.fetch_reposts()

                # Detect and log new reposts
                await self.detect_and_log_new_reposts(current_reposts)

                # Success - reset failure counter and return
                self.consecutive_failures = 0
                self.check_count += 1
                return

            except (AttributeError, ConnectionError) as e:
                # Browser connection corruption - restart container
                retry_count += 1
                self.consecutive_failures += 1
                error_msg = f"Browser connection issue (attempt {retry_count}/{max_retries}): {e}"
                print(f"Error: {error_msg}")
                self.logger.log_error(error_msg)

                if retry_count >= max_retries or self.consecutive_failures >= 2:
                    print("Multiple connection failures detected - restarting container...")
                    self.logger.log_info("Triggering container restart due to connection failures")
                    await self.cleanup()
                    print("Exiting for container restart...")
                    sys.exit(0)  # Docker will restart the container

                # Try one more time before container restart
                wait_time = Config.RETRY_DELAY_SECONDS * retry_count
                print(f"Retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)

            except Exception as e:
                retry_count += 1
                self.consecutive_failures += 1
                error_msg = f"Check failed (attempt {retry_count}/{max_retries}): {e}"
                print(f"Error: {error_msg}")
                self.logger.log_error(error_msg)

                # If we've had multiple consecutive failures, restart container
                if self.consecutive_failures >= 3:
                    print(f"Detected {self.consecutive_failures} consecutive failures - restarting container...")
                    self.logger.log_info("Triggering container restart due to consecutive failures")
                    await self.cleanup()
                    print("Exiting for container restart...")
                    sys.exit(0)  # Docker will restart the container

                if retry_count < max_retries:
                    # Use exponential backoff
                    wait_time = Config.RETRY_DELAY_SECONDS * (2 ** (retry_count - 1))
                    print(f"Retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)

        # All retries failed - restart container
        print("All retry attempts failed - restarting container...")
        self.logger.log_error("All retry attempts failed - triggering container restart")
        await self.cleanup()
        sys.exit(0)  # Docker will restart the container

    async def run(self):
        """Main run loop - periodically check for new reposts."""
        self.is_running = True

        try:
            # Initialize browser
            await self.initialize_browser()

            # Optional: Login if credentials provided
            if Config.TIKTOK_EMAIL and Config.TIKTOK_PASSWORD:
                await self.login()

            # Display stats
            stats = self.state_manager.get_stats()
            print(f"\nStarting monitoring...")
            print(f"Previously seen reposts: {stats['total_seen']}")
            print(f"Total reposts logged: {stats['total_logged']}")
            print(f"Last check: {stats['last_check']}")
            print(f"Check interval: {Config.CHECK_INTERVAL_MINUTES} minute(s)\n")

            self.logger.log_info(f"Started monitoring @{Config.TIKTOK_USERNAME}")

            # Main monitoring loop
            while self.is_running:
                print(f"\n{'='*60}")
                print(f"Checking for new reposts at {time.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"{'='*60}")

                await self.check_for_new_reposts()

                if self.is_running:
                    print(f"\nNext check in {Config.CHECK_INTERVAL_MINUTES} minute(s)...")
                    # Sleep in smaller intervals to allow for graceful shutdown
                    for _ in range(Config.CHECK_INTERVAL_MINUTES * 60):
                        if not self.is_running:
                            break
                        await asyncio.sleep(1)

        except KeyboardInterrupt:
            print("\n\nReceived interrupt signal, shutting down...")
            self.logger.log_info("Received interrupt signal, shutting down")

        except Exception as e:
            error_msg = f"Fatal error in main loop: {e}"
            print(f"\nError: {error_msg}")
            self.logger.log_error(error_msg)
            raise

        finally:
            await self.cleanup()

    async def cleanup(self):
        """Clean up resources."""
        print("\nCleaning up resources...")
        self.is_running = False

        try:
            if self.page:
                await self.page.close()

            if self.context:
                await self.context.close()

            if self.browser:
                await self.browser.close()

            if self.playwright:
                await self.playwright.stop()
        except Exception as e:
            print(f"Error during cleanup: {e}")

        print("Cleanup complete")
        self.logger.log_info("Application stopped")

    def stop(self):
        """Stop the monitoring loop."""
        print("\nStopping monitoring...")
        self.is_running = False


async def main():
    """Main entry point."""
    logger_instance = TikTokRepostLogger()

    # Set up signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        print(f"\nReceived signal {signum}")
        logger_instance.stop()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Run the logger
    await logger_instance.run()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutdown complete")
        sys.exit(0)
    except Exception as e:
        print(f"\nFatal error: {e}")
        sys.exit(1)
