"""Storage package — handles settings and stats persistence."""

import os
import shutil
import sys
from pathlib import Path


# Default directory name under %APPDATA% for frozen builds
_APP_DATA_DIR_NAME = "Pomodoro Timer"


def get_data_dir() -> Path:
    """Return the stable data directory for user settings and stats.

    Under PyInstaller onefile, uses ``%APPDATA%/Pomodoro Timer/`` so data
    survives across restarts instead of being written to a temporary
    ``_MEI*`` directory.

    Under source, returns the project-relative ``data/`` directory.
    """
    if getattr(sys, "frozen", False):
        # Running as a PyInstaller bundle — use the user's roaming profile
        appdata = os.environ.get("APPDATA", "")
        if appdata:
            return Path(appdata) / _APP_DATA_DIR_NAME

    # Source runtime — resolve from *this file's* location.
    # __file__ is  src/storage/__init__.py
    #    .parent  → src/storage/
    #    .parent.parent  → src/
    #    .parent.parent.parent  → project root
    return Path(__file__).resolve().parent.parent.parent / "data"


def migrate_old_data(old_dir: Path, new_dir: Path):
    """Copy settings.json / stats.json from *old_dir* or exe-adjacent
    ``data/`` to *new_dir* if *new_dir* is empty.  Silently skips when
    nothing to migrate.
    """
    if new_dir.exists():
        return  # nothing to do — target already has data

    # Collect candidate old directories; under a frozen build also check
    # next to the .exe in case the user placed the bundle in the project
    # directory that already has a populated data/ folder.
    candidates = [old_dir]
    if getattr(sys, "frozen", False):
        candidates.append(Path(sys.executable).parent / "data")

    files = ("settings.json", "stats.json")
    for candidate in candidates:
        if not candidate.exists():
            continue
        for name in files:
            src = candidate / name
            if src.exists():
                new_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, new_dir / name)
        break  # only use the first candidate that exists
