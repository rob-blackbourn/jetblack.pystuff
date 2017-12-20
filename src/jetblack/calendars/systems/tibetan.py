import math
from jetblack.calendars.utils import amod
from jetblack.calendars.systems.gregorian import GregorianDate
from jetblack.calendars.utils import reduce_cond, list_range, final_int
from jetblack.calendars.months import MonthOfYear

class TibetanDate(object):
    
    EPOCH = GregorianDate(-127, MonthOfYear.DECEMBER, 7).toordinal()

    def __init__(self, year, month, leap_month, day, leap_day):
        self.year = year
        self.month = month
        self.leap_month = leap_month
        self.day = day
        self.leap_day = leap_day
    
    def to_tuple(self):
        return (self.year, self.month, self.leap_month, self.day, self.leap_day)
    
    def toordinal(self):
        """Return the ordinal date corresponding to this Tibetan lunar date."""
        months = int(math.floor((804/65 * (self.year - 1)) + (67/65 * self.month) + (-1 if self.leap_month else 0) + 64/65))
        days = (30 * months) + self.day
        mean = (days * 11135/11312) -30 + (0 if self.leap_day else -1) + 1071/1616
        solar_anomaly = ((days * 13/4824) + 2117/4824) % 1
        lunar_anomaly = ((days * 3781/105840) + 2837/15120) % 1
        sun  = -self.sun_equation(12 * solar_anomaly)
        moon = self.moon_equation(28 * lunar_anomaly)
        return int(math.floor(self.EPOCH + mean + sun + moon))

    @classmethod
    def fromordinal(cls, ordinal):
        """Return the Tibetan lunar date corresponding to ordinal date, 'ordinal'."""
        cap_Y = 365 + 4975/18382
        years = int(math.ceil((ordinal - cls.EPOCH) / cap_Y))
        year0 = final_int(years, lambda y:(ordinal >= TibetanDate(y, 1, False, 1, False).toordinal()))
        month0 = final_int(1, lambda m: (ordinal >= TibetanDate(year0, m, False, 1, False).toordinal()))
        est = ordinal - TibetanDate(year0, month0, False, 1, False).toordinal()
        day0 = final_int(est -2, lambda d: (ordinal >= TibetanDate(year0, month0, False, d, False).toordinal()))
        leap_month = (day0 > 30)
        day = amod(day0, 30)
        if day > day0:
            temp = month0 - 1
        elif leap_month:
            temp = month0 + 1
        else:
            temp = month0
        month = amod(temp, 12)
        
        if day > day0 and month0 == 1:
            year = year0 - 1
        elif leap_month and month0 == 12:
            year = year0 + 1
        else:
            year = year0
        leap_day = ordinal == TibetanDate(year, month, leap_month, day, True).toordinal()
        return TibetanDate(year, month, leap_month, day, leap_day)

    @classmethod        
    def sun_equation(cls, alpha):
        """Return the interpolated tabular sine of solar anomaly, 'alpha'."""
        if alpha > 6:
            return -cls.sun_equation(alpha - 6)
        elif alpha > 3:
            return cls.sun_equation(6 - alpha)
        elif isinstance(alpha, int):
            return [0, 6/60, 10/60, 11/60][alpha]
        else:
            return ((alpha % 1) * cls.sun_equation(int(math.ceil(alpha)))) + ((-alpha % 1) * cls.sun_equation(int(math.floor(alpha))))

    @classmethod
    def moon_equation(cls, alpha):
        """Return the interpolated tabular sine of lunar anomaly, 'alpha'."""
        if alpha > 14:
            return -cls.moon_equation(alpha - 14)
        elif alpha > 7:
            return cls.moon_equation(14 -alpha)
        elif isinstance(alpha, int):
            return [0, 5/60, 10/60, 15/60, 19/60, 22/60, 24/60, 25/60][alpha]
        else:
            return ((alpha % 1) * cls.moon_equation(int(math.ceil(alpha)))) + ((-alpha % 1) * cls.moon_equation(int(math.floor(alpha))))

    @classmethod
    def is_leap_month(cls, month, year):
        """Return True if 'month' is leap in Tibetan year, 'year'."""
        return month == TibetanDate.fromordinal(TibetanDate(year, month, True, 2, False).toordinal()).month

    @classmethod
    def losar(cls, year):
        """Return the  ordinal date of Tibetan New Year (Losar)
        in Tibetan year, 'year'."""
        t_leap = cls.is_leap_month(1, year)
        return TibetanDate(year, 1, t_leap, 1, False).toordinal()

    @classmethod
    def new_year(cls, gregorian_year):
        """Return the list of ordinal dates of Tibetan New Year in
        Gregorian year, 'gregorian_year'."""
        dec31  = GregorianDate.year_end(gregorian_year)
        t_year = cls.fromordinal(dec31).year
        return list_range([cls.losar(t_year - 1), cls.losar(t_year)], GregorianDate.year_range(gregorian_year))

    def __eq__(self, other):
        return isinstance(other, TibetanDate) and all(map(lambda (x,y): x == y, zip(self.to_tuple(), other.to_tuple())))
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __lt__(self, other):
        return isinstance(other, TibetanDate) and reduce_cond(lambda _, (x, y): x < y, lambda r, (x, y): not r and x == y, zip(self.to_tuple(), other.to_tuple()), False)
    
    def __le__(self, other):
        return isinstance(other, TibetanDate) and reduce_cond(lambda _, (x, y): x <= y, lambda r, (x, y): not r and x == y, zip(self.to_tuple(), other.to_tuple()), False)
    
    def __gt__(self, other):
        return isinstance(other, TibetanDate) and reduce_cond(lambda _, (x, y): x > y, lambda r, (x, y): not r and x == y, zip(self.to_tuple(), other.to_tuple()), False)
    
    def __ge__(self, other):
        return isinstance(other, TibetanDate) and reduce_cond(lambda _, (x, y): x >= y, lambda r, (x, y): not r and x == y, zip(self.to_tuple(), other.to_tuple()), False)
