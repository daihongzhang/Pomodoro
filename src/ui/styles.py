"""QSS stylesheet for the Pomodoro timer application."""

MAIN_STYLE = """
QMainWindow {
    background-color: #f5f0e8;
}

/* --- Timer Display --- */
#timerLabel {
    font-size: 72px;
    font-weight: bold;
    color: #d35f5f;
    font-family: "Segoe UI", "Arial", sans-serif;
    padding: 10px;
}

/* --- Phase Tabs --- */
QPushButton#phaseWork, QPushButton#phaseBreak, QPushButton#phaseLongBreak {
    border: none;
    border-radius: 15px;
    padding: 6px 18px;
    font-size: 14px;
    font-weight: bold;
    color: #888;
    background-color: transparent;
}

QPushButton#phaseWork:checked,
QPushButton#phaseBreak:checked,
QPushButton#phaseLongBreak:checked {
    background-color: #d35f5f;
    color: white;
}

/* --- Control Buttons --- */
/* All three buttons share the same base sizing */
QPushButton#btnStart,
QPushButton#btnPause,
QPushButton#btnReset,
QPushButton#btnSkip {
    font-size: 14px;
    padding: 8px 20px;
    border-radius: 18px;
}

/* Start button (primary CTA) - slightly more horizontal padding */
QPushButton#btnStart,
QPushButton#btnPause {
    background-color: #d35f5f;
    color: white;
    border: none;
    font-weight: bold;
    padding-right: 28px;
    padding-left: 28px;
}

QPushButton#btnStart:hover,
QPushButton#btnPause:hover {
    background-color: #c04a4a;
}

QPushButton#btnReset,
QPushButton#btnSkip {
    background-color: transparent;
    color: #999;
    border: 1px solid #ccc;
}

QPushButton#btnReset:hover,
QPushButton#btnSkip:hover {
    background-color: #e8e0d6;
    color: #666;
}

/* --- Stats Footer --- */
#statsLabel {
    font-size: 14px;
    color: #666;
    padding: 10px;
}

/* --- Menu Bar --- */
QMenuBar {
    background-color: #f5f0e8;
    border-bottom: 1px solid #ddd;
    padding: 2px;
}

QMenuBar::item:selected {
    background-color: #d35f5f;
    color: white;
    border-radius: 4px;
}

QMenu {
    background-color: white;
    border: 1px solid #ddd;
    border-radius: 6px;
    padding: 4px;
}

QMenu::item {
    padding: 6px 24px;
    border-radius: 4px;
}

QMenu::item:selected {
    background-color: #f0e6dc;
    color: #333;
}

/* --- Settings Dialog --- */
#settingsGroup {
    font-size: 14px;
    font-weight: bold;
    color: #555;
    border: 1px solid #ddd;
    border-radius: 8px;
    margin-top: 10px;
    padding: 16px;
}

QLineEdit, QSpinBox {
    border: 1px solid #ccc;
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 14px;
    background-color: white;
}

QLineEdit:focus, QSpinBox:focus {
    border-color: #d35f5f;
}

QCheckBox {
    font-size: 14px;
    color: #555;
    spacing: 8px;
}

QPushButton#btnSave {
    background-color: #d35f5f;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 8px 24px;
    font-size: 14px;
    font-weight: bold;
}

QPushButton#btnSave:hover {
    background-color: #c04a4a;
}

QPushButton#btnCancel {
    background-color: transparent;
    color: #666;
    border: 1px solid #ccc;
    border-radius: 6px;
    padding: 8px 24px;
    font-size: 14px;
}

QPushButton#btnCancel:hover {
    background-color: #f0f0f0;
}

/* --- System Tray --- */
QSystemTrayIcon {
    /* platform-dependent, nothing much to style here */
}
"""


def apply_style(app):
    """Apply the stylesheet to the QApplication."""
    app.setStyleSheet(MAIN_STYLE)
