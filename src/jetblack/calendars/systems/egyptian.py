import math
from jetblack.calendars.ymd import YearMonthDay
from jetblack.calendars.systems.julian import JulianDay

class EgyptianDate(YearMonthDay):

    EPOCH = JulianDay(1448638).toordinal()    

    def __init__(self, year, month, day):
        super().__init__(year, month, day)
        
    def toordinal(self):
        return self.EPOCH + 365 * (self.year - 1) + 30 * (self.month - 1) + self.day - 1

    @classmethod
    def fromordinal(cls, ordinal):
        """Return the Egyptian date corresponding to ordinal"""
        days = ordinal - cls.EPOCH
        year = 1 + int(math.floor(days / 365))
        month = 1 + int(math.floor((days % 365) / 30))
        day = days - 365 * (year - 1) - 30 * (month - 1) + 1
        return EgyptianDate(year, month, day)
