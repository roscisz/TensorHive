from enum import IntEnum

class LogFileCleanupAction(IntEnum):
    REMOVE = 0
    HIDE = 1
    RENAME = 2
    LEAVE = 3
