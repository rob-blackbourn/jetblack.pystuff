import math

class Clock(object):
    
    def __init__(self, hour, minute, second):
        self.hour = hour
        self.minute = minute
        self.second = second

    def to_time(self):
        """Return time of day from clock time."""
        return(1/24 * (self.hour + ((self.minute + (self.second / 60)) / 60)))

    @classmethod
    def from_moment(cls, tee):
        """Return clock time hour:minute:second from moment 'tee'."""
        time = cls.time_from_moment(tee)
        hour = int(math.floor(time * 24))
        minute = int(math.floor((time * 24 * 60) % 60))
        second = (time * 24 * 60 * 60) % 60
        return Clock(hour, minute, second)

    @classmethod
    def ordinal_from_moment(cls, tee):
        """Return ordinal date from moment 'tee'."""
        return int(math.floor(tee))
    
    @classmethod
    def time_from_moment(cls, tee):
        """Return time from moment 'tee'."""
        return tee % 1

    @classmethod
    def days_from_hours(cls, hours):
        """Return the number of days given x hours."""
        return hours / 24
    
    @classmethod
    def days_from_seconds(cls, seconds):
        """Return the number of days given x seconds."""
        return seconds / 24 / 60 / 60