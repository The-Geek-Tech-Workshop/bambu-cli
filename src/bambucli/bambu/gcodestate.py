from enum import Enum


class GcodeState(Enum):
    FAILED = "failed"
    FINISH = "finish"
    IDLE = "idle"
    INIT = "init"
    OFFLINE = "offline"
    PAUSE = "pause"
    PREPARE = "prepare"
    RUNNING = "running"
    SLICING = "slicing"
    UNKNOWN = "unknown"
