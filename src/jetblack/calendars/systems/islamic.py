import math
from mpmath import mpf
from jetblack.calendars.timemath import Clock
from jetblack.calendars.systems.julian import JulianDate
from jetblack.calendars.location import Location
from jetblack.calendars.systems.gregorian import GregorianDate
from jetblack.calendars.ymd import YearMonthDay
from jetblack.calendars.utils import list_range
from jetblack.calendars.datemath import MonthOfYear
from jetblack.calendars.lunar import MEAN_SYNODIC_MONTH

class IslamicDate(YearMonthDay):

    EPOCH = JulianDate(JulianDate.ce(622), MonthOfYear.JULY, 16).toordinal()

    def __init__(self, year, month, day):
        super().__init__(year, month, day)
    
    def toordinal(self):
        raise NotImplementedError()

    @classmethod
    def fromordinal(cls, ordinal):
        raise NotImplementedError()

    @classmethod    
    def is_leap_year(cls, year):
        """Return True if year is an Islamic leap year."""
        return 14 + 11 * year % 30 < 11

    @classmethod
    def in_gregorian(cls, month, day, gregorian_year):
        """Return list of the ordinal dates of Islamic month 'month', day 'day' that
        occur in Gregorian year 'gregorian_year'."""
        jan1  = GregorianDate.new_year(gregorian_year)
        y     = cls.fromordinal(jan1).year
        date1 = IslamicDate(y, month, day).toordinal()
        date2 = IslamicDate(y + 1, month, day).toordinal()
        date3 = IslamicDate(y + 2, month, day).toordinal()
        return list_range([date1, date2, date3], GregorianDate.year_range(gregorian_year))
    
    @classmethod
    def mawlid_an_nabi(cls, gregorian_year):
        """Return list of ordinal dates of Mawlid_an_Nabi occurring in Gregorian
        year 'gregorian_year'."""
        return cls.in_gregorian(3, 12, gregorian_year)

class ArithmeticIslamicDate(IslamicDate):
    
    def __init__(self, year, month, day):
        super().__init__(year, month, day)
    
    def toordinal(self):
        """Return ordinal date equivalent to this Islamic date."""
        return (self.EPOCH - 1 +
                (self.year - 1) * 354  +
                int(math.floor((3 + 11 * self.year) / 30)) +
                29 * (self.month - 1) +
                int(math.floor(self.month / 2)) +
                self.day)

    @classmethod
    def fromordinal(cls, ordinal):
        """Return Islamic date (year month day) corresponding to ordinal date 'ordinal'."""
        year       = int(math.floor((30 * (ordinal - cls.EPOCH) + 10646) / 10631))
        prior_days = ordinal - ArithmeticIslamicDate(year, 1, 1).toordinal()
        month      = int(math.floor((11 * prior_days + 330) % 325))
        day        = ordinal - ArithmeticIslamicDate(year, month, 1).toordinal() + 1
        return ArithmeticIslamicDate(year, month, day)
        

class ObservationalIslamicDate(IslamicDate):
    
    # (Cairo, Egypt).
    LOCATION = Location(mpf(30.1), mpf(31.3), 200, Clock.days_from_hours(2))
    
    def __init__(self, year, month, day):
        IslamicDate.__init__(self, year, month, day)

    def toordinal(self):
        """Return ordinal date equivalent to Observational Islamic date, i_date."""
        midmonth = self.EPOCH + int(math.floor((((self.year - 1) * 12) + self.month - 0.5) * MEAN_SYNODIC_MONTH))
        return (self.LOCATION.phasis_on_or_before(midmonth) + self.day - 1)

    @classmethod
    def fromordinal(cls, ordinal):
        """Return Observational Islamic date (year month day)
        corresponding to ordinal date, 'ordinal'."""
        crescent = cls.LOCATION.phasis_on_or_before(ordinal)
        elapsed_months = int(round((crescent - cls.EPOCH) / MEAN_SYNODIC_MONTH))
        year = int(math.floor(elapsed_months / 12)) + 1
        month = (elapsed_months % 12) + 1
        day = (ordinal - crescent) + 1
        return ObservationalIslamicDate(year, month, day)
