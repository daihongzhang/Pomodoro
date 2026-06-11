"""Statistics manager - tracks daily pomodoro counts."""

import json
from datetime import date
from pathlib import Path

from src.storage import get_data_dir, migrate_old_data

DATA_DIR = get_data_dir()
STATS_FILE = DATA_DIR / "stats.json"
OLD_DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"


class StatsManager:
    """Singleton that records how many pomodoros were completed each day."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._loaded = False
        return cls._instance

    def __init__(self):
        if self._loaded:
            return
        self._loaded = True
        self._stats: dict[str, int] = {}
        self._load()

    def _load(self):
        """Load stats from JSON file."""
        if not STATS_FILE.exists():
            # Migration: copy old project-relative data if it exists
            migrate_old_data(OLD_DATA_DIR, DATA_DIR)
        if not STATS_FILE.exists():
            self._stats = {}
            self._save()
            return
        try:
            with open(STATS_FILE, "r", encoding="utf-8") as f:
                self._stats = json.load(f)
        except (json.JSONDecodeError, OSError):
            self._stats = {}
            self._save()

    def _save(self):
        """Write stats to JSON file."""
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(STATS_FILE, "w", encoding="utf-8") as f:
            json.dump(self._stats, f, indent=2, ensure_ascii=False)

    def increment_today(self):
        """Add one completed pomodoro to today's count."""
        today = date.today().isoformat()  # "2026-06-06"
        self._stats[today] = self._stats.get(today, 0) + 1
        self._save()

    def get_today_count(self) -> int:
        """Get the number of pomodoros completed today."""
        today = date.today().isoformat()
        return self._stats.get(today, 0)

    def get_weekly_counts(self) -> dict[str, int]:
        """Get counts for the last 7 days (including today)."""
        from datetime import timedelta
        today = date.today()
        result = {}
        for i in range(6, -1, -1):
            day = (today - timedelta(days=i)).isoformat()
            result[day] = self._stats.get(day, 0)
        return result

    def get_total_count(self) -> int:
        """Get total pomodoros across all history."""
        return sum(self._stats.values())

    def reset_all(self):
        """Clear all stats."""
        self._stats = {}
        self._save()
