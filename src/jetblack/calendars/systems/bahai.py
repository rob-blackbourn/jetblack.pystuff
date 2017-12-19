from mpmath import mpf
import math
from jetblack.calendars.location import Location
from jetblack.calendars.datemath import MonthOfYear, Season
from jetblack.calendars.timemath import Clock
from jetblack.calendars.solar import MEAN_TROPICAL_YEAR, solar_longitude, estimate_prior_solar_longitude
from jetblack.calendars.utils import reduce_cond, next_int
from jetblack.calendars.systems.gregorian import GregorianDate

class BahaiDate(object):

    EPOCH = GregorianDate(1844, MonthOfYear.MARCH, 21).toordinal()
    HAIFA = Location(mpf(32.82), 35, 0, Clock.days_from_hours(2))
    AYYAM_I_HA = 0
    
    def __init__(self, major, cycle, year, month, day):
        self.major = major
        self.cycle = cycle
        self.year = year
        self.month = month
        self.day = day
    
    def to_tuple(self):
        return (self.major, self.cycle, self.year, self.month, self.day)
    
    def toordinal(self):
        raise NotImplementedError()

    @classmethod
    def fromordinal(cls, ordinal):
        raise NotImplementedError()

    @classmethod    
    def new_year(cls, gregorian_year):
        """Return ordinal date of Bahai New Year in Gregorian year, 'gregorian_year'."""
        return GregorianDate(gregorian_year, MonthOfYear.MARCH, 21).toordinal()
    

    @classmethod    
    def sunset_in_haifa(cls, ordinal):
        """Return universal time of sunset of evening
        before ordinal date in Haifa."""
        return cls.HAIFA.universal_from_standard(cls.HAIFA.sunset(ordinal))

    def __eq__(self, other):
        return isinstance(other, BahaiDate) and all(map(lambda (x,y): x == y, zip(self.to_tuple(), other.to_tuple())))
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __lt__(self, other):
        return isinstance(other, BahaiDate) and reduce_cond(lambda _, (x, y): x < y, lambda r, (x, y): not r and x == y, zip(self.to_tuple(), other.to_tuple()), False)
    
    def __le__(self, other):
        return isinstance(other, BahaiDate) and reduce_cond(lambda _, (x, y): x <= y, lambda r, (x, y): not r and x == y, zip(self.to_tuple(), other.to_tuple()), False)
    
    def __gt__(self, other):
        return isinstance(other, BahaiDate) and reduce_cond(lambda _, (x, y): x > y, lambda r, (x, y): not r and x == y, zip(self.to_tuple(), other.to_tuple()), False)
    
    def __ge__(self, other):
        return isinstance(other, BahaiDate) and reduce_cond(lambda _, (x, y): x >= y, lambda r, (x, y): not r and x == y, zip(self.to_tuple(), other.to_tuple()), False)

class WesternBahaiDate(BahaiDate):
    
    def __init__(self, major, cycle, year, month, day):
        super().__init__(major, cycle, year, month, day)
    
    def toordinal(self):
        """Return ordinal date equivalent to the Bahai date, b_date."""
        g_year = (361 * (self.major - 1) +
                  19 * (self.cycle - 1)  +
                  self.year - 1 +
                  GregorianDate.to_year(self.EPOCH))
        if (self.month == self.AYYAM_I_HA):
            elapsed_months = 342
        elif (self.month == 19):
            if (GregorianDate.is_leap_year(g_year + 1)):
                elapsed_months = 347
            else:
                elapsed_months = 346
        else:
            elapsed_months = 19 * (self.month - 1)
    
        return GregorianDate(g_year, MonthOfYear.MARCH, 20).toordinal() + elapsed_months + self.day

    @classmethod
    def fromordinal(cls, ordinal):
        """Return Bahai date [major, cycle, year, month, day] corresponding
        to ordinal date."""
        g_year = GregorianDate.to_year(ordinal)
        start  = GregorianDate.to_year(cls.EPOCH)
        years  = (g_year - start -
                  (1 if (ordinal <= 
                      GregorianDate(g_year, MonthOfYear.MARCH, 20).toordinal()) else 0))
        major  = 1 + int(math.floor(years / 361))
        cycle  = 1 + int(math.floor((years % 361) / 19))
        year   = 1 + years % 19
        days   = ordinal - WesternBahaiDate(major, cycle, year, 1, 1).toordinal()

        # month
        if ordinal >= WesternBahaiDate(major, cycle, year, 19, 1).toordinal():
            month = 19
        elif ordinal >= WesternBahaiDate(major, cycle, year, cls.AYYAM_I_HA, 1).toordinal():
            month = cls.AYYAM_I_HA
        else:
            month = 1 + int(math.floor(days / 19))
    
        day = ordinal + 1 - WesternBahaiDate(major, cycle, year, month, 1).toordinal()
    
        return WesternBahaiDate(major, cycle, year, month, day)

class FutureBahaiDate(BahaiDate):
    
    def __init(self, major, cycle, year, month, day):
        super().__init(major, cycle, year, month, day)
    
    def toordinal(self):
        """Return ordinal date of Bahai date, b_date."""
        years = (361 * (self.major - 1)) + (19 * (self.cycle - 1)) + self.year
        if self.month == 19:
            return self.new_year_on_or_before(self.EPOCH + int(math.floor(MEAN_TROPICAL_YEAR * (years + 1/2)))) - 20 + self.day
        elif self.month == self.AYYAM_I_HA:
            return self.new_year_on_or_before(self.EPOCH + int(math.floor(MEAN_TROPICAL_YEAR * (years - 1/2)))) + 341 + self.day
        else:
            return self.new_year_on_or_before(self.EPOCH + int(math.floor(MEAN_TROPICAL_YEAR * (years - 1/2)))) + (19 * (self.month - 1)) + self.day - 1
    
    @classmethod
    def fromordinal(cls, ordinal):
        """Return Future Bahai date corresponding to ordinal date."""
        new_year = cls.new_year_on_or_before(ordinal)
        years    = int(round((new_year - cls.EPOCH) / MEAN_TROPICAL_YEAR))
        major    = 1 + int(math.floor(years / 361))
        cycle    = 1 + int(math.floor((years % 361) / 19))
        year     = 1 + years % 19
        days     = ordinal - new_year
    
        if ordinal >= FutureBahaiDate(major, cycle, year, 19, 1).toordinal():
            month = 19
        elif ordinal >= FutureBahaiDate(major, cycle, year, cls.AYYAM_I_HA, 1).toordinal():
            month = cls.AYYAM_I_HA
        else:
            month = 1 + int(math.floor(days / 19))
    
        day = ordinal + 1 - FutureBahaiDate(major, cycle, year, month, 1).toordinal()
    
        return FutureBahaiDate(major, cycle, year, month, day)

    @classmethod    
    def new_year_on_or_before(cls, ordinal):
        """Return ordinal date of Future Bahai New Year on or
        before ordinal date."""
        approx = estimate_prior_solar_longitude(Season.SPRING, cls.sunset_in_haifa(ordinal))
        return next_int(int(math.floor(approx)) - 1, lambda day: solar_longitude(cls.sunset_in_haifa(day)) <= Season.SPRING + 2)

    @classmethod    
    def feast_of_ridvan(cls, gregorian_year):
        """Return ordinal date of Feast of Ridvan in Gregorian year year, 'gregorian_year'."""
        years = gregorian_year - GregorianDate.to_year(cls.EPOCH)
        major = 1 + int(math.floor(years / 361))
        cycle = 1 + int(math.floor((years % 361) / 19))
        year = 1 + years % 19
        return FutureBahaiDate(major, cycle, year, 2, 13).toordinal()
