"""Application entry point - initializes QApplication, applies style, shows main window."""

import sys
import ctypes
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import QApplication

from src.ui.main_window import MainWindow
from src.ui.styles import apply_style
from src.single_instance import try_activate_existing, SingleInstanceServer

# Unique AppUserModelID — tells Windows this is our own app, not "Python",
# so the taskbar uses our icon instead of the Python launcher icon.
# Must be set before QApplication is created.
APP_USER_MODEL_ID = "ClaudeProjects.PomodoroTimer.1.0"
try:
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_USER_MODEL_ID)
except Exception:
    pass  # non-fatal; icon may fall back to Python default

ICON_PATH = Path(__file__).resolve().parent / "resources" / "tomato.ico"


def _load_icon() -> QIcon | None:
    """Load the tomato icon, print debug info on failure."""
    if not ICON_PATH.exists():
        print(f"[Pomodoro] Icon not found: {ICON_PATH.resolve()}", file=sys.stderr)
        return None
    icon = QIcon(str(ICON_PATH))
    if icon.isNull():
        print(f"[Pomodoro] Icon loaded but isNull(): {ICON_PATH.resolve()}", file=sys.stderr)
        return None
    return icon


def create_app() -> QApplication:
    """Create and configure the QApplication."""
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("Pomodoro Timer")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("ClaudeProjects")

    # Window / taskbar icon
    icon = _load_icon()
    if icon is not None:
        app.setWindowIcon(icon)

    # Default font
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    # Apply stylesheet
    apply_style(app)

    return app


def run():
    """Launch the application (single-instance)."""
    app = create_app()

    # ----- Single-instance check -----
    # Must happen AFTER QApplication creation (QLocalSocket needs an event loop).
    if try_activate_existing():
        # Another instance is already running — it will show its window.
        sys.exit(0)

    # This is the first instance — start the IPC server so future launches
    # can find us.
    ipc_server = SingleInstanceServer()
    # ---------------------------------

    window = MainWindow()

    # Also set the icon on the window itself (title bar, Alt+Tab)
    icon = _load_icon()
    if icon is not None:
        window.setWindowIcon(icon)

    # When the second instance asks us to show up …
    ipc_server.show_requested.connect(window.show_from_second_instance)

    # Clean up the named pipe when the app exits properly
    app.aboutToQuit.connect(ipc_server.cleanup)

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    run()
