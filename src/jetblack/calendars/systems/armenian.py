from jetblack.calendars.ymd import YearMonthDay
from jetblack.calendars.systems.egyptian import EgyptianDate

class ArmenianDate(YearMonthDay):

    EPOCH = 201443
    
    def __init__(self, year, month, day):
        super().__init__(year, month, day)

    def toordinal(self):
        """Return the ordinal date."""
        return (self.EPOCH + EgyptianDate(self.year, self.month, self.day).toordinal() - EgyptianDate.EPOCH)

    @classmethod
    def fromordinal(cls, ordinal):
        """Return the Armenian ordinal date corresponding to ordinal date."""
        ymd = EgyptianDate.fromordinal(ordinal + (EgyptianDate.EPOCH - cls.EPOCH))
        return ArmenianDate(ymd.year, ymd.month, ymd.day)