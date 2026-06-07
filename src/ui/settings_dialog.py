"""Settings dialog for configuring Pomodoro durations and preferences."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox,
    QCheckBox, QPushButton, QGroupBox, QFormLayout,
    QDialogButtonBox, QWidget,
)

from src.storage.settings import SettingsManager


class SettingsDialog(QDialog):
    """Dialog for editing application settings."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._settings = SettingsManager()
        self.setWindowTitle("设置")
        self.setMinimumWidth(380)
        self.setModal(True)
        self._setup_ui()
        self._load_settings()

    def _setup_ui(self):
        """Build the dialog layout."""
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        # --- Duration settings ---
        duration_group = QGroupBox("⏱ 时长设置")
        duration_layout = QFormLayout(duration_group)
        duration_layout.setSpacing(8)

        self._spin_work = QSpinBox()
        self._spin_work.setRange(1, 120)
        self._spin_work.setSuffix(" 分钟")
        self._spin_work.setFixedWidth(120)
        duration_layout.addRow("工作时间:", self._spin_work)

        self._spin_break = QSpinBox()
        self._spin_break.setRange(1, 60)
        self._spin_break.setSuffix(" 分钟")
        self._spin_break.setFixedWidth(120)
        duration_layout.addRow("短休息:", self._spin_break)

        self._spin_long_break = QSpinBox()
        self._spin_long_break.setRange(1, 120)
        self._spin_long_break.setSuffix(" 分钟")
        self._spin_long_break.setFixedWidth(120)
        duration_layout.addRow("长休息:", self._spin_long_break)

        self._spin_long_interval = QSpinBox()
        self._spin_long_interval.setRange(1, 20)
        self._spin_long_interval.setSuffix(" 个番茄")
        self._spin_long_interval.setFixedWidth(120)
        duration_layout.addRow("长休息间隔:", self._spin_long_interval)

        layout.addWidget(duration_group)

        # --- Behavior settings ---
        behavior_group = QGroupBox("⚙ 行为设置")
        behavior_layout = QVBoxLayout(behavior_group)
        behavior_layout.setSpacing(6)

        self._chk_top = QCheckBox("窗口总在最前")
        behavior_layout.addWidget(self._chk_top)

        self._chk_sound = QCheckBox("完成时播放提示音")
        behavior_layout.addWidget(self._chk_sound)

        self._chk_tray = QCheckBox("开始计时时自动最小化到托盘")
        behavior_layout.addWidget(self._chk_tray)

        layout.addWidget(behavior_group)

        # --- Buttons ---
        layout.addSpacing(8)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self._btn_save = QPushButton("保存")
        self._btn_save.setObjectName("btnSave")
        self._btn_save.clicked.connect(self._on_save)

        self._btn_cancel = QPushButton("取消")
        self._btn_cancel.setObjectName("btnCancel")
        self._btn_cancel.clicked.connect(self.reject)

        btn_layout.addWidget(self._btn_cancel)
        btn_layout.addWidget(self._btn_save)
        layout.addLayout(btn_layout)

    def _load_settings(self):
        """Populate fields from current settings."""
        self._spin_work.setValue(self._settings.get("work_duration"))
        self._spin_break.setValue(self._settings.get("break_duration"))
        self._spin_long_break.setValue(self._settings.get("long_break_duration"))
        self._spin_long_interval.setValue(self._settings.get("pomodoros_until_long_break"))
        self._chk_top.setChecked(self._settings.get("always_on_top"))
        self._chk_sound.setChecked(self._settings.get("sound_enabled"))
        self._chk_tray.setChecked(self._settings.get("minimize_to_tray_on_start"))

    def _on_save(self):
        """Validate and save settings, then close."""
        self._settings.set_many(
            work_duration=self._spin_work.value(),
            break_duration=self._spin_break.value(),
            long_break_duration=self._spin_long_break.value(),
            pomodoros_until_long_break=self._spin_long_interval.value(),
            always_on_top=self._chk_top.isChecked(),
            sound_enabled=self._chk_sound.isChecked(),
            minimize_to_tray_on_start=self._chk_tray.isChecked(),
        )
        self.accept()
