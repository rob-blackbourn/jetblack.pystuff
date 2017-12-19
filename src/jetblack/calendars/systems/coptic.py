import math
from jetblack.calendars.ymd import YearMonthDay
from jetblack.calendars.datemath import MonthOfYear
from jetblack.calendars.systems.julian import JulianDate
from jetblack.calendars.systems.gregorian import GregorianDate
from jetblack.calendars.utils import list_range

class CopticDate(YearMonthDay):

    EPOCH = JulianDate(JulianDate.ce(284), MonthOfYear.AUGUST, 29).toordinal()
    
    def __init__(self, year, month, day):
        super().__init__(year, month, day)

    @classmethod
    def is_leap_year(year):
        """Return True if Coptic year 'c_year' is a leap year
        in the Coptic calendar."""
        return year % 4 == 3
    
    def toordinal(self):
        """Return the ordinal date of Coptic date."""
        return (self.EPOCH - 1  +
                365 * (self.year - 1)  +
                int(math.floor(self.year / 4)) +
                30 * (self.month - 1)  +
                self.day)

    @classmethod
    def fromordinal(cls, ordinal):
        """Return the Coptic date equivalent of ordinal date 'ordinal'."""
        year  = int(math.floor(((4 * (ordinal - cls.EPOCH)) + 1463) / 1461))
        month = 1 + int(math.floor((ordinal - CopticDate(year, 1, 1).toordinal()) / 30))
        day   = ordinal + 1 - CopticDate(year, month, 1).toordinal()
        return CopticDate(year, month, day)

    @classmethod
    def in_gregorian(cls, coptic_month, coptic_day, gregorian_year):
        """Return the list of the ordinal dates of Coptic month 'coptic_month',
        day 'coptic_day' that occur in Gregorian year 'gregorian_year'."""
        jan1  = GregorianDate.new_year(gregorian_year)
        y     = cls.fromordinal(jan1).year
        date1 = CopticDate(y, coptic_month, coptic_day).toordinal()
        date2 = CopticDate(y+1, coptic_month, coptic_day).toordinal()
        return list_range([date1, date2], GregorianDate.year_range(gregorian_year))

    @classmethod    
    def christmas(cls, gregorian_year):
        """Retuen the list of zero or one ordinal dates of Coptic Christmas
        dates in Gregorian year 'gregorian_year'."""
        return cls.coptic_in_gregorian(4, 29, gregorian_year)
