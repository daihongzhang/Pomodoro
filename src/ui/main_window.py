"""Main window of the Pomodoro timer application."""

import sys

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction, QIcon, QPixmap, QPainter, QColor, QFont
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QCheckBox, QMenu, QSystemTrayIcon, QMessageBox,
    QApplication, QSizePolicy,
)

from src.timer.state import TimerState, Phase
from src.timer.worker import TimerWorker
from src.storage.settings import SettingsManager
from src.storage.stats import StatsManager
from src.ui.settings_dialog import SettingsDialog
from src.ui.styles import apply_style


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self._settings = SettingsManager()
        self._stats = StatsManager()
        self._worker = TimerWorker(self)
        self._is_quitting = False

        self._setup_ui()
        self._setup_menu()
        self._setup_tray()
        self._connect_signals()
        self._update_ui()

        # Load geometry
        self.resize(360, 380)
        self.setMinimumSize(300, 320)

        self._apply_always_on_top(self._settings.get("always_on_top"))

    # ---- UI Setup ----

    def _setup_ui(self):
        """Build the central widget layout."""
        self.setWindowTitle("Pomodoro Timer")
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(8)
        layout.setContentsMargins(30, 10, 30, 20)

        # Phase selector row
        phase_row = QHBoxLayout()
        phase_row.setAlignment(Qt.AlignCenter)
        phase_row.setSpacing(6)

        self._btn_work = QPushButton("🍅 工作")
        self._btn_work.setObjectName("phaseWork")
        self._btn_work.setCheckable(True)
        self._btn_work.setChecked(True)
        self._btn_work.clicked.connect(lambda: self._switch_phase(Phase.WORK))

        self._btn_break = QPushButton("☕ 休息")
        self._btn_break.setObjectName("phaseBreak")
        self._btn_break.setCheckable(True)
        self._btn_break.clicked.connect(lambda: self._switch_phase(Phase.BREAK))

        self._btn_long_break = QPushButton("☕ 长休")
        self._btn_long_break.setObjectName("phaseLongBreak")
        self._btn_long_break.setCheckable(True)
        self._btn_long_break.clicked.connect(lambda: self._switch_phase(Phase.LONG_BREAK))

        phase_row.addWidget(self._btn_work)
        phase_row.addWidget(self._btn_break)
        phase_row.addWidget(self._btn_long_break)
        layout.addLayout(phase_row)

        layout.addSpacing(16)

        # Timer display
        self._lbl_timer = QLabel("25:00")
        self._lbl_timer.setObjectName("timerLabel")
        self._lbl_timer.setAlignment(Qt.AlignCenter)
        self._lbl_timer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self._lbl_timer)

        layout.addSpacing(12)

        # Control buttons row
        ctrl_row = QHBoxLayout()
        ctrl_row.setAlignment(Qt.AlignCenter)
        ctrl_row.setSpacing(12)

        self._btn_reset = QPushButton("◀ 重置")
        self._btn_reset.setObjectName("btnReset")

        self._btn_start = QPushButton("▶ 开始")
        self._btn_start.setObjectName("btnStart")

        self._btn_skip = QPushButton("跳过 ▶")
        self._btn_skip.setObjectName("btnSkip")

        ctrl_row.addWidget(self._btn_reset)
        ctrl_row.addWidget(self._btn_start)
        ctrl_row.addWidget(self._btn_skip)
        layout.addLayout(ctrl_row)

        layout.addSpacing(16)

        # Stats footer
        self._lbl_stats = QLabel()
        self._lbl_stats.setObjectName("statsLabel")
        self._lbl_stats.setAlignment(Qt.AlignCenter)
        layout.addWidget(self._lbl_stats)

        # Connect control buttons
        self._btn_start.clicked.connect(self._on_start_clicked)
        self._btn_reset.clicked.connect(self._on_reset_clicked)
        self._btn_skip.clicked.connect(self._on_skip_clicked)

        # Set initial durations from settings
        self._worker.reload_durations()
        self._update_timer_display()

    def _setup_menu(self):
        """Build the menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("文件")
        self._act_settings = QAction("设置...", self)
        self._act_settings.triggered.connect(self._open_settings)
        file_menu.addAction(self._act_settings)

        file_menu.addSeparator()

        self._act_always_top = QAction("总在最前", self)
        self._act_always_top.setCheckable(True)
        self._act_always_top.setChecked(self._settings.get("always_on_top"))
        self._act_always_top.triggered.connect(self._toggle_always_top)
        file_menu.addAction(self._act_always_top)

        file_menu.addSeparator()

        self._act_quit = QAction("退出", self)
        self._act_quit.triggered.connect(self._quit_app)
        file_menu.addAction(self._act_quit)

        # Help menu
        help_menu = menubar.addMenu("帮助")
        self._act_about = QAction("关于...", self)
        self._act_about.triggered.connect(self._show_about)
        help_menu.addAction(self._act_about)

    def _setup_tray(self):
        """Set up system tray icon and context menu."""
        self._tray_icon = QSystemTrayIcon(self)
        self._tray_icon.setToolTip("Pomodoro Timer")

        # Create a simple colored icon programmatically
        tray_pixmap = QPixmap(32, 32)
        tray_pixmap.fill(Qt.transparent)
        painter = QPainter(tray_pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QColor("#d35f5f"))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(2, 2, 28, 28)
        painter.setFont(QFont("Segoe UI", 14, QFont.Bold))
        painter.setPen(QColor("white"))
        painter.drawText(tray_pixmap.rect(), Qt.AlignCenter, "P")
        painter.end()
        self._tray_icon.setIcon(QIcon(tray_pixmap))

        # Tray context menu
        tray_menu = QMenu()
        self._act_show_hide = QAction("显示/隐藏", self)
        self._act_show_hide.triggered.connect(self._toggle_visible)
        tray_menu.addAction(self._act_show_hide)

        tray_menu.addSeparator()

        self._act_tray_start = QAction("开始", self)
        self._act_tray_start.triggered.connect(self._on_start_clicked)
        tray_menu.addAction(self._act_tray_start)

        self._act_tray_reset = QAction("重置", self)
        self._act_tray_reset.triggered.connect(self._on_reset_clicked)
        tray_menu.addAction(self._act_tray_reset)

        tray_menu.addSeparator()

        self._act_tray_quit = QAction("退出程序", self)
        self._act_tray_quit.triggered.connect(self._quit_app)
        tray_menu.addAction(self._act_tray_quit)

        self._tray_icon.setContextMenu(tray_menu)
        self._tray_icon.activated.connect(self._on_tray_activated)
        self._tray_icon.show()

    # ---- Signal Connections ----

    def _connect_signals(self):
        """Connect TimerWorker signals to UI updates."""
        self._worker.tick.connect(self._on_tick)
        self._worker.phase_changed.connect(self._on_phase_changed)
        self._worker.state_changed.connect(self._on_state_changed)
        self._worker.finished.connect(self._on_finished)

    # ---- Slots ----

    def _on_tick(self, remaining: int):
        """Update the timer display every second."""
        self._update_timer_display()
        self._update_tray_tooltip()

    def _on_phase_changed(self, phase_value: str):
        """Update phase selector buttons when the phase changes."""
        phase = Phase(phase_value)
        self._btn_work.setChecked(phase == Phase.WORK)
        self._btn_break.setChecked(phase == Phase.BREAK)
        self._btn_long_break.setChecked(phase == Phase.LONG_BREAK)
        self._update_timer_display()

    def _on_state_changed(self, state: TimerState):
        """Update UI when timer state changes."""
        self._update_ui()

    def _on_finished(self):
        """Handle a phase completing (countdown reaches zero)."""
        # Record completed pomodoro
        if self._worker.phase == Phase.WORK:
            self._stats.increment_today()
            self._update_stats()

        # Flash notification
        self._show_notification()

        # Play sound if enabled
        if self._settings.get("sound_enabled"):
            self._play_sound()

        # Auto-start next phase after a brief delay
        QTimer.singleShot(1500, self._worker.start)

    def _on_start_clicked(self):
        """Handle start/pause button click."""
        started = False
        match self._worker.state:
            case TimerState.IDLE | TimerState.FINISHED:
                self._worker.start()
                started = True
            case TimerState.RUNNING:
                self._worker.pause()
            case TimerState.PAUSED:
                self._worker.resume()
                started = True

        if started and self._settings.get("minimize_to_tray_on_start"):
            self.hide()

    def _on_reset_clicked(self):
        """Handle reset button click."""
        self._worker.reset()
        self._update_timer_display()

    def _on_skip_clicked(self):
        """Handle skip button click."""
        self._worker.skip()
        self._update_timer_display()

    def _switch_phase(self, phase: Phase):
        """Manually switch to a different phase (only when idle)."""
        if self._worker.state != TimerState.IDLE:
            return
        self._worker.stop()  # reset everything
        # Set internal phase directly (stop() resets to WORK, so override)
        self._worker._phase = phase
        self._worker.reload_durations()
        self._worker.phase_changed.emit(phase.value)
        self._update_timer_display()

    def _toggle_always_top(self, checked: bool):
        """Toggle window always-on-top."""
        self._apply_always_on_top(checked, persist=True)

    def _open_settings(self):
        """Open the settings dialog."""
        dialog = SettingsDialog(self)
        if dialog.exec():
            self._worker.reload_durations()
            self._update_timer_display()
            self._apply_always_on_top(self._settings.get("always_on_top"))

    def _apply_always_on_top(self, checked: bool, persist: bool = False, force: bool = False):
        """Apply the topmost flag only when it actually changes."""
        checked = bool(checked)

        if hasattr(self, "_act_always_top") and self._act_always_top.isChecked() != checked:
            self._act_always_top.blockSignals(True)
            self._act_always_top.setChecked(checked)
            self._act_always_top.blockSignals(False)

        if persist:
            self._settings.set("always_on_top", checked)

        current = bool(self.windowFlags() & Qt.WindowStaysOnTopHint)
        if not force and current == checked:
            return

        self.setWindowFlag(Qt.WindowStaysOnTopHint, checked)
        if self.isVisible():
            self.show()
            self.raise_()
            self.activateWindow()

    def show_from_second_instance(self):
        """Called when a second-instance process asks us to show the window."""
        self.showNormal()
        self.raise_()
        self.activateWindow()

    def _toggle_visible(self):
        """Toggle window visibility."""
        if self.isVisible():
            self.hide()
        else:
            self.show()
            self.raise_()
            self.activateWindow()

    def _quit_app(self):
        """Exit the application from explicit menu/tray commands."""
        self._is_quitting = True
        self._tray_icon.hide()
        QApplication.instance().quit()

    def _minimize_to_tray_from_close(self):
        """Hide the window after the close button chooses tray behavior."""
        self.hide()
        self._tray_icon.showMessage(
            "Pomodoro Timer",
            "应用已最小化到系统托盘",
            QSystemTrayIcon.Information,
            2000,
        )

    def _ask_close_button_action(self) -> str:
        """Ask what the window close button should do."""
        dialog = QMessageBox(self)
        dialog.setWindowTitle("关闭 Pomodoro Timer")
        dialog.setText("请选择关闭按钮的操作")
        dialog.setIcon(QMessageBox.Icon.Question)

        minimize_button = dialog.addButton(
            "最小化到托盘",
            QMessageBox.ButtonRole.AcceptRole,
        )
        exit_button = dialog.addButton(
            "退出程序",
            QMessageBox.ButtonRole.DestructiveRole,
        )
        cancel_button = dialog.addButton(
            "取消",
            QMessageBox.ButtonRole.RejectRole,
        )

        remember_choice = QCheckBox("记住我的选择")
        dialog.setCheckBox(remember_choice)
        dialog.exec()

        clicked_button = dialog.clickedButton()
        if clicked_button == minimize_button:
            action = "minimize_to_tray"
        elif clicked_button == exit_button:
            action = "exit"
        elif clicked_button == cancel_button:
            action = "cancel"
        else:
            action = "cancel"

        if remember_choice.isChecked() and action in {"minimize_to_tray", "exit"}:
            self._settings.set("close_button_action", action)

        return action

    def _get_close_button_action(self) -> str:
        """Resolve the saved close-button action."""
        action = self._settings.get("close_button_action")
        if action in {"ask", "minimize_to_tray", "exit"}:
            return action
        return "ask"

    def _on_tray_activated(self, reason):
        """Handle tray icon activation (click)."""
        if reason == QSystemTrayIcon.DoubleClick:
            self._toggle_visible()

    def _show_notification(self):
        """Show a desktop notification when a phase completes."""
        phase_name = self._worker.phase.display_name()
        phase_icon = self._worker.phase.icon()
        if self._worker.phase == Phase.WORK:
            msg = "工作完成！休息一下吧 ☕"
        else:
            msg = "休息结束！继续加油 💪"

        # Show tray notification
        self._tray_icon.showMessage(
            f"{phase_icon} {phase_name} 完成",
            msg,
            QSystemTrayIcon.Information,
            5000,
        )

        # Flash window to get attention
        QApplication.alert(self, 3000)

    def _play_sound(self):
        """Play a system completion sound.

        Priority order (Windows):
          1. PlaySound("SystemAsterisk") — async, doesn't block the timer
          2. MessageBeep(MB_ICONASTERISK)
          3. QApplication.beep() — cross-platform Qt fallback

        Non-Windows platforms skip directly to QApplication.beep().
        All exceptions are swallowed — sound is best-effort and must
        never affect timer operation or tray notification.
        """
        try:
            if sys.platform == "win32":
                import winsound

                # 1. Play the system "Asterisk" sound asynchronously.
                #    Async is important: timer ticks must not pause.
                try:
                    winsound.PlaySound(
                        "SystemAsterisk",
                        winsound.SND_ALIAS | winsound.SND_ASYNC,
                    )
                    return
                except Exception:
                    pass

                # 2. Fallback: simple message beep
                try:
                    winsound.MessageBeep(winsound.MB_ICONASTERISK)
                    return
                except Exception:
                    pass

            # 3. Last resort: Qt cross-platform beep
            QApplication.beep()
        except Exception:
            pass  # best-effort; never crash the timer

    def _show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "关于 Pomodoro Timer",
            "Pomodoro Timer v1.0\n\n"
            "基于番茄工作法的桌面计时器\n"
            "25 分钟工作 + 5 分钟休息\n\n"
            "使用 PySide6 构建",
        )

    # ---- UI Updates ----

    def _update_ui(self):
        """Update button states and labels based on timer state."""
        match self._worker.state:
            case TimerState.IDLE:
                self._btn_start.setText("▶ 开始")
                self._btn_start.setObjectName("btnStart")
            case TimerState.RUNNING:
                self._btn_start.setText("⏸ 暂停")
                self._btn_start.setObjectName("btnPause")
            case TimerState.PAUSED:
                self._btn_start.setText("▶ 继续")
                self._btn_start.setObjectName("btnStart")
            case TimerState.FINISHED:
                self._btn_start.setText("▶ 下一步")
                self._btn_start.setObjectName("btnStart")

        # Refresh styling after object name change
        self._btn_start.style().unpolish(self._btn_start)
        self._btn_start.style().polish(self._btn_start)

        self._update_stats()

    def _update_timer_display(self):
        """Update the timer label with formatted time."""
        self._lbl_timer.setText(self._worker.format_time())

    def _update_stats(self):
        """Update the stats footer."""
        count = self._stats.get_today_count()
        self._lbl_stats.setText(f"🍅 今日完成: {count}")

    def _update_tray_tooltip(self):
        """Update the tray icon tooltip with current time/phase."""
        phase_icon = self._worker.phase.icon()
        phase_name = self._worker.phase.display_name()
        time_str = self._worker.format_time()
        state_icon = "▶" if self._worker.state == TimerState.RUNNING else "⏸"
        self._tray_icon.setToolTip(f"{state_icon} {phase_icon} {phase_name} {time_str}")

    # ---- Window Events ----

    def closeEvent(self, event):
        """Handle the close button based on user preference."""
        if self._is_quitting:
            event.accept()
            return

        action = self._get_close_button_action()
        if action == "ask":
            action = self._ask_close_button_action()

        if action == "minimize_to_tray":
            event.ignore()
            self._minimize_to_tray_from_close()
        elif action == "exit":
            self._is_quitting = True
            self._tray_icon.hide()
            event.accept()
            QTimer.singleShot(0, QApplication.instance().quit)
        else:
            event.ignore()
