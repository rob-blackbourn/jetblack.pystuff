from jetblack.calendars.datemath import MonthOfYear, Season
from jetblack.calendars.trigonometry import angle
from jetblack.calendars.utils import ifloor, iround, quotient
from jetblack.calendars.location import Location
from jetblack.calendars.systems.gregorian import GregorianDate
from jetblack.calendars.timemath import Clock
from jetblack.calendars.ymd import YearMonthDay
from jetblack.calendars.utils import next_int
from jetblack.calendars.solar import MEAN_TROPICAL_YEAR, estimate_prior_solar_longitude, solar_longitude

class FrenchDate(YearMonthDay):

    #"""Date of start of the French Revolutionary calendar."""
    EPOCH = GregorianDate(1792, MonthOfYear.SEPTEMBER, 22).toordinal()
    PARIS = Location(angle(48, 50, 11), angle(2, 20, 15), 27, Clock.days_from_hours(1))
    
    def __init__(self, year, month, day):
        super().__init__(year, month, day)

    def toordinal(self):
        """Return ordinal date of French Revolutionary date, f_date"""
        new_year = self.new_year_on_or_before(ifloor(self.EPOCH + 180 + MEAN_TROPICAL_YEAR * (self.year - 1)))
        return new_year - 1 + 30 * (self.month - 1) + self.day

    @classmethod
    def fromordinal(cls, ordinal):
        """Return French Revolutionary date of ordinal date, 'ordinal'."""
        new_year = cls.new_year_on_or_before(ordinal)
        year  = iround((new_year - cls.EPOCH) / MEAN_TROPICAL_YEAR) + 1
        month = quotient(ordinal - new_year, 30) + 1
        day   = ((ordinal - new_year) % 30) + 1
        return FrenchDate(year, month, day)

    @classmethod        
    def midnight_in_paris(cls, ordinal):
        """Return Universal Time of true midnight at the end of
           ordinal date, ordinal."""
        # tricky bug: I was using midDAY!!! So French Revolutionary was failing...
        return cls.PARIS.universal_from_standard(cls.PARIS.midnight(ordinal + 1))

    @classmethod    
    def new_year_on_or_before(cls, ordinal):
        """Return ordinal date of French Revolutionary New Year on or
           before ordinal, ordinal."""
        approx = estimate_prior_solar_longitude(Season.AUTUMN, cls.midnight_in_paris(ordinal))
        return next_int(ifloor(approx) - 1, lambda day: Season.AUTUMN <= solar_longitude(cls.midnight_in_paris(day)))
    
    @classmethod
    def is_arithmetic_leap_year(cls, f_year):
        """Return True if year, f_year, is a leap year on the French
           Revolutionary calendar."""
        return f_year % 4 == 0 and f_year % 400 not in [100, 200, 300] and f_year % 4000 != 0
    
    def toordinal_arithmetic(self):
        """Return ordinal date of French Revolutionary date, f_date."""
        return (self.EPOCH - 1         +
                365 * (self.year - 1)         +
                quotient(self.year - 1, 4)    -
                quotient(self.year - 1, 100)  +
                quotient(self.year - 1, 400)  -
                quotient(self.year - 1, 4000) +
                30 * (self.month - 1)         +
                self.day)

    @classmethod    
    def fromordinal_arithmetic(cls, ordinal):
        """Return French Revolutionary date [year, month, day] of ordinal
           ordinal, ordinal."""
        approx = quotient(ordinal - cls.EPOCH + 2, 1460969/4000) + 1
        year   = ((approx - 1)
                  if (ordinal < FrenchDate(approx, 1, 1).toordinal_arithmetic())
                  else approx)
        month  = 1 + quotient(ordinal - FrenchDate(year, 1, 1).toordinal_arithmetic(), 30)
        day    = ordinal -  FrenchDate(year, month, 1).toordinal_arithmetic() + 1
        return FrenchDate(year, month, day)