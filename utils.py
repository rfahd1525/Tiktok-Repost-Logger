"""
Utility functions for TikTok Repost Logger.
Handles file operations, data persistence, and logging.
"""

import json
import os
from datetime import datetime
from typing import Set, Dict, Any


class StateManager:
    """Manages persistent state for tracking seen reposts."""

    def __init__(self, state_file_path: str):
        """
        Initialize state manager.

        Args:
            state_file_path: Path to JSON file storing state
        """
        self.state_file_path = state_file_path
        self.state = self._load_state()

    def _load_state(self) -> Dict[str, Any]:
        """
        Load state from file.

        Returns:
            Dictionary containing state data
        """
        if os.path.exists(self.state_file_path):
            try:
                with open(self.state_file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load state file: {e}")
                return self._create_empty_state()
        else:
            return self._create_empty_state()

    def _create_empty_state(self) -> Dict[str, Any]:
        """Create empty state structure."""
        return {
            'seen_repost_ids': [],
            'last_check': None,
            'total_reposts_logged': 0
        }

    def _save_state(self):
        """Save current state to file."""
        try:
            with open(self.state_file_path, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Error: Could not save state file: {e}")

    def get_seen_repost_ids(self) -> Set[str]:
        """
        Get set of previously seen repost IDs.

        Returns:
            Set of repost video IDs
        """
        return set(self.state.get('seen_repost_ids', []))

    def add_repost_id(self, repost_id: str):
        """
        Add a repost ID to the seen list.

        Args:
            repost_id: Video ID of the repost
        """
        seen_ids = self.get_seen_repost_ids()
        seen_ids.add(repost_id)
        self.state['seen_repost_ids'] = list(seen_ids)
        self.state['total_reposts_logged'] = self.state.get('total_reposts_logged', 0) + 1
        self._save_state()

    def update_last_check(self):
        """Update the timestamp of last successful check."""
        self.state['last_check'] = datetime.now().isoformat()
        self._save_state()

    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about logged reposts.

        Returns:
            Dictionary with stats
        """
        return {
            'total_seen': len(self.state.get('seen_repost_ids', [])),
            'total_logged': self.state.get('total_reposts_logged', 0),
            'last_check': self.state.get('last_check')
        }


class Logger:
    """Handles logging of repost information to file."""

    def __init__(self, log_file_path: str):
        """
        Initialize logger.

        Args:
            log_file_path: Path to log file
        """
        self.log_file_path = log_file_path

    def log_repost(self, video_url: str, video_id: str = None):
        """
        Log a new repost to the log file.

        Args:
            video_url: URL of the reposted video
            video_id: Optional video ID for reference
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] New repost detected: {video_url}"

        if video_id:
            log_entry += f" (ID: {video_id})"

        log_entry += "\n"

        try:
            with open(self.log_file_path, 'a', encoding='utf-8') as f:
                f.write(log_entry)
            print(log_entry.strip())
        except IOError as e:
            print(f"Error: Could not write to log file: {e}")

    def log_info(self, message: str):
        """
        Log an informational message.

        Args:
            message: Message to log
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] INFO: {message}\n"

        try:
            with open(self.log_file_path, 'a', encoding='utf-8') as f:
                f.write(log_entry)
            print(log_entry.strip())
        except IOError as e:
            print(f"Error: Could not write to log file: {e}")

    def log_error(self, message: str):
        """
        Log an error message.

        Args:
            message: Error message to log
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] ERROR: {message}\n"

        try:
            with open(self.log_file_path, 'a', encoding='utf-8') as f:
                f.write(log_entry)
            print(log_entry.strip())
        except IOError as e:
            print(f"Error: Could not write to log file: {e}")


def extract_video_id_from_url(url: str) -> str:
    """
    Extract content ID from TikTok URL (works for both videos and photos).

    Args:
        url: TikTok video or photo URL

    Returns:
        Content ID string
    """
    # TikTok URLs typically look like:
    # https://www.tiktok.com/@username/video/1234567890
    # https://www.tiktok.com/@username/photo/1234567890
    # or https://vm.tiktok.com/XXXXXXXXX/
    if '/video/' in url:
        return url.split('/video/')[-1].split('?')[0].split('/')[0]
    elif '/photo/' in url:
        return url.split('/photo/')[-1].split('?')[0].split('/')[0]
    elif 'vm.tiktok.com' in url or 'vt.tiktok.com' in url:
        # For short URLs, use the entire path as ID
        return url.split('/')[-1].split('?')[0]
    else:
        # Fallback: use the entire URL as ID
        return url

def format_video_url(video_id: str, username: str = None) -> str:
    """
    Format a proper TikTok video URL.

    Args:
        video_id: Video ID
        username: Optional username

    Returns:
        Formatted TikTok video URL
    """
    if video_id.startswith('http'):
        return video_id

    if username:
        return f"https://www.tiktok.com/@{username}/video/{video_id}"
    else:
        return f"https://www.tiktok.com/video/{video_id}"
