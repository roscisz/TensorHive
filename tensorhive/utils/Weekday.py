from enum import Enum


class Weekday(Enum):
    """Helper enum used mainly in RestrictionSchedule class to provide more legible way of specifying schedules"""
    Monday = 1
    Tuesday = 2
    Wednesday = 3
    Thursday = 4
    Friday = 5
    Saturday = 6
    Sunday = 7

    def to_str(self):
        return ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][self.value - 1]
