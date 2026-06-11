"""Timer worker - handles the countdown logic using QTimer."""

from PySide6.QtCore import QObject, QTimer, Signal

from src.timer.state import TimerState, Phase
from src.storage.settings import SettingsManager


class TimerWorker(QObject):
    """Manages the Pomodoro countdown with second-precision ticks.

    Signals:
        tick(remaining_seconds: int) — emitted every second while running
        phase_changed(phase: str) — emitted when work/break phase switches
        state_changed(state: TimerState) — emitted on state transitions
        finished() — emitted when a countdown reaches zero
    """

    tick = Signal(int)
    phase_changed = Signal(str)
    state_changed = Signal(object)  # TimerState
    finished = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._settings = SettingsManager()
        self._timer = QTimer(self)
        self._timer.setInterval(1000)  # 1 second
        self._timer.timeout.connect(self._on_tick)

        self._state = TimerState.IDLE
        self._phase = Phase.WORK
        self._remaining = 0          # seconds remaining in current countdown
        self._total = 0              # total seconds for current phase
        self._completed_pomodoros = 0  # completed work sessions this cycle

    # --- Properties ---

    @property
    def state(self) -> TimerState:
        return self._state

    @state.setter
    def state(self, value: TimerState):
        self._state = value
        self.state_changed.emit(value)

    @property
    def phase(self) -> Phase:
        return self._phase

    @property
    def remaining(self) -> int:
        return self._remaining

    @property
    def completed_pomodoros(self) -> int:
        return self._completed_pomodoros

    def _get_phase_duration(self, phase: Phase) -> int:
        match phase:
            case Phase.WORK:
                return self._settings.get("work_duration") * 60
            case Phase.BREAK:
                return self._settings.get("break_duration") * 60
            case Phase.LONG_BREAK:
                return self._settings.get("long_break_duration") * 60

    def format_time(self, seconds: int = None) -> str:
        """Format seconds as MM:SS."""
        if seconds is None:
            seconds = self._remaining
        m, s = divmod(seconds, 60)
        return f"{m:02d}:{s:02d}"

    # --- Public API ---

    def start(self):
        """Start or resume the current phase countdown."""
        if self._state == TimerState.IDLE:
            # Phase/duration should already be set by _on_phase_complete or init;
            # just fill them if somehow still zero (fresh launch).
            if self._remaining <= 0:
                self._total = self._get_phase_duration(self._phase)
                self._remaining = self._total
            self.phase_changed.emit(self._phase.value)

        elif self._state == TimerState.PAUSED:
            pass  # keep remaining as-is

        elif self._state == TimerState.FINISHED:
            self._advance_phase()

        self.state = TimerState.RUNNING
        self._timer.start()

    def pause(self):
        """Pause the countdown."""
        if self._state == TimerState.RUNNING:
            self._timer.stop()
            self.state = TimerState.PAUSED

    def resume(self):
        """Resume from paused state."""
        if self._state == TimerState.PAUSED:
            self.state = TimerState.RUNNING
            self._timer.start()

    def reset(self):
        """Reset the current phase to its full duration."""
        self._timer.stop()
        self._remaining = self._total
        self.state = TimerState.IDLE
        self.tick.emit(self._remaining)

    def skip(self):
        """Skip to the next phase immediately."""
        self._timer.stop()
        self._on_phase_complete()

    def stop(self):
        """Fully stop the timer and return to idle."""
        self._timer.stop()
        self._remaining = 0
        self._total = 0
        self._phase = Phase.WORK
        self._completed_pomodoros = 0
        self.state = TimerState.IDLE
        self.phase_changed.emit(self._phase.value)
        self.tick.emit(0)

    def reload_durations(self):
        """Reload durations from settings (called after settings change)."""
        if self._state in (TimerState.IDLE, TimerState.FINISHED):
            self._total = self._get_phase_duration(self._phase)
            self._remaining = self._total
            self.tick.emit(self._remaining)

    # --- Internal ---

    def _on_tick(self):
        """Called every second by QTimer."""
        self._remaining -= 1
        self.tick.emit(self._remaining)

        if self._remaining <= 0:
            self._timer.stop()
            self.state = TimerState.FINISHED
            self.finished.emit()

    def _on_phase_complete(self):
        """Handle completion of a phase and switch to the next."""
        if self._phase == Phase.WORK:
            self._completed_pomodoros += 1
            long_break_interval = self._settings.get("pomodoros_until_long_break")
            if self._completed_pomodoros >= long_break_interval:
                self._phase = Phase.LONG_BREAK
                self._completed_pomodoros = 0
            else:
                self._phase = Phase.BREAK
        else:
            # Break/Long break is over → back to work
            self._phase = Phase.WORK

        self._total = self._get_phase_duration(self._phase)
        self._remaining = self._total
        self.state = TimerState.IDLE
        self.phase_changed.emit(self._phase.value)
        self.tick.emit(self._remaining)

    def _advance_phase(self):
        """Advance to the next phase (called from start() after finished)."""
        self._on_phase_complete()


