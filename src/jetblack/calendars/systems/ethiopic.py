from jetblack.calendars.systems.julian import JulianDate
from jetblack.calendars.systems.coptic import CopticDate
from jetblack.calendars.ymd import YearMonthDay
from jetblack.calendars.months import MonthOfYear

class EthiopicDate(YearMonthDay):
    
    EPOCH = JulianDate(JulianDate.ce(8), MonthOfYear.AUGUST, 29).toordinal()

    def __init__(self, year, month, day):
        super().__init__(year, month, day)

    def toordinal(self):
        """Return the ordinal date corresponding to Ethiopic date 'e_date'."""
        return (self.EPOCH + CopticDate(self.year, self.month, self.day).toordinal() - CopticDate.EPOCH)

    @classmethod
    def fromordinal(cls, ordinal):
        """Return the Ethiopic date equivalent of ordinal date 'ordinal'."""
        ymd = CopticDate.fromordinal(ordinal + (CopticDate.EPOCH - cls.EPOCH))
        return EthiopicDate(ymd.year, ymd.month, ymd.day)