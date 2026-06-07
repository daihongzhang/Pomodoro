"""Timer state machine."""

from enum import Enum, auto


class TimerState(Enum):
    IDLE = auto()
    RUNNING = auto()
    PAUSED = auto()
    FINISHED = auto()


class Phase(Enum):
    WORK = "work"
    BREAK = "break"
    LONG_BREAK = "long_break"

    def display_name(self) -> str:
        return {
            Phase.WORK: "工作",
            Phase.BREAK: "短休息",
            Phase.LONG_BREAK: "长休息",
        }[self]

    def icon(self) -> str:
        return {
            Phase.WORK: "🍅",
            Phase.BREAK: "☕",
            Phase.LONG_BREAK: "☕",
        }[self]
