import math
from mpmath import mpf
from jetblack.calendars.months import MonthOfYear
from jetblack.calendars.seasons import Season
from jetblack.calendars.timemath import Clock
from jetblack.calendars.location import Location
from jetblack.calendars.ymd import YearMonthDay
from jetblack.calendars.utils import next_int
from jetblack.calendars.solar import estimate_prior_solar_longitude,\
    solar_longitude, MEAN_TROPICAL_YEAR
from jetblack.calendars.systems.julian import JulianDate
from jetblack.calendars.systems.gregorian import GregorianDate

class PersianDate(YearMonthDay):

    EPOCH = JulianDate(JulianDate.ce(622), MonthOfYear.MARCH, 19).toordinal()
    TEHRAN = Location(mpf(35.68), mpf(51.42), 1100, Clock.days_from_hours(3 + 1/2))
    
    def __init__(self, year, month, day):
        super().__init__(year, month, day)

    @classmethod        
    def midday_in_tehran(cls, date):
        """Return  Universal time of midday on ordinal date, date, in Tehran."""
        return cls.TEHRAN.universal_from_standard(cls.TEHRAN.midday(date))
    
    @classmethod        
    def new_year_on_or_before(cls, date):
        """Return the ordinal date of Astronomical Persian New Year on or
        before ordinal date, ordinal."""
        approx = estimate_prior_solar_longitude(Season.SPRING, cls.midday_in_tehran(date))
        return next_int(int(math.floor(approx)) - 1, lambda day: (solar_longitude(cls.midday_in_tehran(day)) <= (Season.SPRING + 2)))

    def toordinal(self):
        """Return ordinal date of Astronomical Persian date, p_date."""
        temp = (self.year - 1) if (0 < self.year) else self.year
        new_year = self.new_year_on_or_before(self.EPOCH + 180 + int(math.floor(MEAN_TROPICAL_YEAR * temp)))
        return ((new_year - 1) +
                ((31 * (self.month - 1)) if (self.month <= 7) else (30 * (self.month - 1) + 6)) +
                self.day)

    @classmethod        
    def fromordinal(cls, ordinal):
        """Return Astronomical Persian date (year month day)
        corresponding to ordinal date, ordinal."""
        new_year = cls.new_year_on_or_before(ordinal)
        y = int(round((new_year - cls.EPOCH) / MEAN_TROPICAL_YEAR)) + 1
        year = y if (0 < y) else (y - 1)
        day_of_year = ordinal - PersianDate(year, 1, 1).toordinal() + 1
        month = int(math.ceil(day_of_year / 31)) if day_of_year <= 186 else int(math.ceil((day_of_year - 6) / 30))
        day = ordinal - (PersianDate(year, month, 1).toordinal() - 1)
        return PersianDate(year, month, day)
    
    @classmethod
    def is_arithmetic_leap_year(cls, p_year):
        """Return True if p_year is a leap year on the Persian calendar."""
        y    = (p_year - 474) if (0 < p_year) else (p_year - 473)
        year =  (y % 2820) + 474
        return  ((year + 38) * 31) % 128 < 31

    # see lines 3934-3958 in calendrica-3.0.cl
    def toordinal_arithmetic(self):
        """Return ordinal date equivalent to Persian date p_date."""
        y      = (self.year - 474) if (0 < self.year) else (self.year - 473)
        year   = (y % 2820) + 474
        temp   = (31 * (self.month - 1)) if (self.month <= 7) else ((30 * (self.month - 1)) + 6)
    
        return ((self.EPOCH - 1) 
                + (1029983 * int(math.floor(y / 2820)))
                + (365 * (year - 1))
                + int(math.floor(((31 * year) - 5) / 128))
                + temp
                + self.day)

    @classmethod
    def to_arithmetic_year(cls, ordinal):
        """Return Persian year corresponding to the ordinal date, ordinal."""
        d0    = ordinal - PersianDate(475, 1, 1).toordinal_arithmetic()
        n2820 = int(math.floor(d0 / 1029983))
        d1    = d0 % 1029983
        y2820 = 2820 if d1 == 1029982 else int(math.floor(((128 * d1) + 46878) / 46751))
        year  = 474 + (2820 * n2820) + y2820
    
        return year if (0 < year) else (year - 1)

    @classmethod
    def fromordinal_arithmetic(cls, ordinal):
        """Return the Persian date corresponding to ordinal date, ordinal."""
        year        = cls.to_arithmetic_year(ordinal)
        day_of_year = 1 + ordinal - PersianDate(year, 1, 1).toordinal_arithmetic()
        month       = int(math.ceil(day_of_year / 31)) if day_of_year <= 186 else int(math.ceil((day_of_year - 6) / 30))
        day = ordinal - PersianDate(year, month, 1).toordinal_arithmetic() +1
        return PersianDate(year, month, day)
    
    @classmethod
    def naw_ruz(cls, g_year):
        """Return the ordinal date of Persian New Year (Naw-Ruz) in Gregorian
           year g_year."""
        persian_year = g_year - GregorianDate.to_year(cls.EPOCH) + 1
        y = (persian_year - 1) if (persian_year <= 0) else persian_year
        return PersianDate(y, 1, 1).toordinal()
