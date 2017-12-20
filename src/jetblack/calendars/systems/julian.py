import math
from mpmath import mpf
from jetblack.calendars.months import MonthOfYear
from jetblack.calendars.weekdays import DayOfWeek, after_weekday
from jetblack.calendars.systems.gregorian import GregorianDate
from jetblack.calendars.ymd import YearMonthDay
from jetblack.calendars.utils import list_range
from jetblack.calendars.datemath import easter

class JulianDay(object):
    
    EPOCH = mpf(-1721424.5)

    def __init__(self, date_from_epoch):
        self.julian_day = date_from_epoch
    
    def toordinal(self):
        return int(math.floor(self.to_moment()))

    @classmethod
    def fromordinal(cls, ordinal):
        return cls.from_moment(ordinal)
    
    def to_moment(self):
        return self.julian_day + self.EPOCH

    @classmethod
    def from_moment(cls, tee):
        return JulianDay(tee - cls.EPOCH)

class ModifiedJulianDay(object):
    
    EPOCH = 678576

    def __init__(self, date_from_epoch):
        self.modified_julian_day = date_from_epoch

    def toordinal(self):
        return self.modified_julian_day + self.EPOCH

    @classmethod
    def fromordinal(cls, ordinal):
        return ModifiedJulianDay(ordinal - cls.EPOCH)

class JulianDate(YearMonthDay):
    
    EPOCH = GregorianDate(0, MonthOfYear.DECEMBER, 30).toordinal()
    
    def __init__(self, year, month, day):
        super().__init__(year, month, day)

    def toordinal(self):
        """Return the ordinal date equivalent to the Julian date 'j_date'."""
        y     = self.year + 1 if self.year < 0 else self.year
        return (self.EPOCH - 1 +
                (365 * (y - 1)) +
                int(math.floor((y - 1) / 4)) +
                int(math.floor((367 * self.month - 362) / 12)) +
                (0 if self.month <= 2 else (-1 if self.is_leap_year(self.year) else -2)) +
                self.day)

    @classmethod
    def fromordinal(cls, ordinal):
        """Return the Julian ordinal_date corresponding to ordinal date 'ordinal'."""
        approx     = int( math.floor(((4 * (ordinal - cls.EPOCH))) + 1464 / 1461))
        year       = approx - 1 if approx <= 0 else approx
        prior_days = ordinal - JulianDate(year, MonthOfYear.JANUARY, 1).toordinal()
        correction = (0 if ordinal < JulianDate(year, MonthOfYear.MARCH, 1).toordinal()
                      else (1 if cls.is_leap_year(year) else 2))
        month      = int(math.floor(((12 * (prior_days + correction) + 373) / 367)))
        day        = 1 + (ordinal - JulianDate(year, month, 1).toordinal())
        return JulianDate(year, month, day)
        
    @classmethod
    def bce(cls, n):
        """Return a negative value to indicate a BCE Julian year."""
        return -n
    
    @classmethod
    def ce(cls, n):
        """Return a positive value to indicate a CE Julian year."""
        return n

    @classmethod
    def is_leap_year(cls, year):
        """Return True if Julian year 'year' is a leap year in
        the Julian calendar."""
        return year % 4 == (0 if year > 0 else 3)

    @classmethod
    def julian_year_from_auc_year(cls, year):
        """Return the Julian year equivalent to AUC year 'year'."""
        return ((year + cls.YEAR_ROME_FOUNDED - 1) 
                if (1 <= year <= (year - cls.YEAR_ROME_FOUNDED))
                else (year + cls.YEAR_ROME_FOUNDED))
    
    @classmethod
    def auc_year_from_julian_year(cls, year):
        """Return the AUC year equivalent to Julian year 'year'."""
        return ((year - cls.YEAR_ROME_FOUNDED - 1)
                if (cls.YEAR_ROME_FOUNDED <= year <= -1)
                else (year - cls.YEAR_ROME_FOUNDED))
    
    
    @classmethod
    def julian_in_gregorian(julian_month, julian_day, gregorian_year):
        """Return the list of the ordinal dates of Julian month 'julian_month', day
        'julian_day' that occur in Gregorian year 'gregorian_year'."""
        jan1 = GregorianDate.new_year(gregorian_year)
        y    = JulianDate.fromordinal(jan1).year
        y_prime = 1 if (y == -1) else (y + 1)
        date1 = JulianDate(y, julian_month, julian_day).toordinal()
        date2 = JulianDate(y_prime, julian_month, julian_day).toordinal()
        return list_range([date1, date2], GregorianDate.year_range(gregorian_year))

    @classmethod
    def eastern_orthodox_christmas(cls, gregorian_year):
        """Return the list of zero or one ordinal dates of Eastern Orthodox Christmas
        in Gregorian year 'gregorian_year'."""
        return cls.julian_in_gregorian(MonthOfYear.DECEMBER, 25, gregorian_year)

#######################################
# ecclesiastical calendars algorithms #
#######################################
def orthodox_easter(gregorian_year):
    """Return ordinal date of Orthodox Easter in Gregorian year g_year."""
    shifted_epact = (14 + 11 * (gregorian_year % 19)) % 30
    j_year        = gregorian_year if gregorian_year > 0 else gregorian_year - 1
    paschal_moon  = JulianDate(j_year, MonthOfYear.APRIL, 19).toordinal() - shifted_epact
    return after_weekday(paschal_moon, DayOfWeek.SUNDAY)

def alt_orthodox_easter(gregorian_year):
    """Return ordinal date of Orthodox Easter in Gregorian year g_year.
    Alternative calculation."""
    paschal_moon = (354 * gregorian_year +
                    30 * int(math.floor(((7 * gregorian_year) + 8) / 19)) +
                    int(math.floor(gregorian_year / 4))  -
                    int(math.floor(gregorian_year / 19)) -
                    273 +
                    GregorianDate.EPOCH)
    return after_weekday(paschal_moon, DayOfWeek.SUNDAY)

# see lines 1429-1431 in calendrica-3.0.cl
def pentecost(gregorian_year):
    """Return ordinal date of Pentecost in Gregorian year gregorian_year."""
    return easter(gregorian_year) + 49

def eastern_orthodox_christmas(year):
    """Return the list of zero or one ordinal dates of Eastern Orthodox Christmas
    in Gregorian year 'year'."""
    return JulianDate.julian_in_gregorian(MonthOfYear.DECEMBER, 25, year)
