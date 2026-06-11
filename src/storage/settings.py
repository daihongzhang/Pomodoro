"""Settings manager - reads/writes settings.json with defaults."""

import json
from pathlib import Path

from src.storage import get_data_dir, migrate_old_data

DATA_DIR = get_data_dir()
SETTINGS_FILE = DATA_DIR / "settings.json"
OLD_DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"

DEFAULT_SETTINGS = {
    "work_duration": 25,        # minutes
    "break_duration": 5,        # minutes
    "long_break_duration": 15,  # minutes
    "pomodoros_until_long_break": 4,
    "always_on_top": False,
    "sound_enabled": True,
    "minimize_to_tray_on_start": False,
    "close_button_action": "ask",
}


class SettingsManager:
    """Singleton that loads/saves user settings from/to a JSON file."""

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
        self._settings = dict(DEFAULT_SETTINGS)
        self._load()

    def _load(self):
        """Load settings from JSON file, merging with defaults."""
        if not SETTINGS_FILE.exists():
            # Migration: copy old project-relative data if it exists
            migrate_old_data(OLD_DATA_DIR, DATA_DIR)
        if not SETTINGS_FILE.exists():
            self._save()  # write defaults
            return
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Merge: keep defaults for any missing keys
            self._settings = {**DEFAULT_SETTINGS, **data}
        except (json.JSONDecodeError, OSError):
            self._settings = dict(DEFAULT_SETTINGS)
            self._save()

    def _save(self):
        """Write current settings to JSON file."""
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(self._settings, f, indent=2, ensure_ascii=False)

    def get(self, key: str):
        """Get a setting value by key."""
        return self._settings.get(key, DEFAULT_SETTINGS.get(key))

    def set(self, key: str, value):
        """Set a setting value and persist to disk."""
        self._settings[key] = value
        self._save()

    def set_many(self, **kwargs):
        """Set multiple settings at once and persist."""
        self._settings.update(kwargs)
        self._save()

    def get_all(self) -> dict:
        """Return a copy of all settings."""
        return dict(self._settings)

    def reset_to_defaults(self):
        """Reset all settings to defaults and persist."""
        self._settings = dict(DEFAULT_SETTINGS)
        self._save()
