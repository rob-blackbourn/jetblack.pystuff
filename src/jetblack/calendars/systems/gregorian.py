import math
import datetime
from fractions import Fraction
from jetblack.calendars.datemath import MonthOfYear, DayOfWeek
from jetblack.calendars.utils import quotient, amod
from jetblack.calendars.datemath import nearest_weekday, on_or_after_weekday,\
    after_weekday
from jetblack.calendars.ymd import YearMonthDay

class GregorianDate(YearMonthDay):    

    EPOCH = 1

    def __init__(self, year, month, day):
        super().__init__(year, month, day)
    
    def toordinal(self):
        """Return the serial date equivalent."""
        return ((self.EPOCH - 1) + 
                (365 * (self.year -1)) + 
                quotient(self.year - 1, 4) - 
                quotient(self.year - 1, 100) + 
                quotient(self.year - 1, 400) + 
                quotient((367 * self.month) - 362, 12) + 
                (0 if self.month <= 2 else (-1 if self.is_leap_year(self.year) else -2)) + self.day)

    @classmethod    
    def fromordinal(cls, ordinal):
        """Return the ordinal_date corresponding to ordinal date."""
        year = cls.to_year(ordinal)
        prior_days = ordinal - cls.new_year(year)
        correction = 0 if ordinal < GregorianDate(year, MonthOfYear.MARCH, 1).toordinal() else (1 if cls.is_leap_year(year) else 2)
        month = quotient((12 * (prior_days + correction)) + 373, 367)
        day = 1 + (ordinal - GregorianDate(year, month, 1).toordinal())
        return GregorianDate(year, month, day)

    def to_date(self):
        return datetime.date(self.year, self.month, self.day)
    
    @classmethod
    def from_date(cls, date):
        return GregorianDate(date.year, date.month, date.day)
    
    @classmethod
    def is_leap_year(cls, year):
        """Return True if 'year' is leap."""
        return year % 4 == 0 and year % 400 not in [100, 200, 300]
    
    @classmethod
    def to_year(cls, ordinal):
        """Return the year corresponding to the ordinal date."""
        d0   = ordinal - cls.EPOCH
        n400 = int(math.floor(d0 / 146097))
        d1   = d0 % 146097
        n100 = quotient(d1, 36524)
        d2   = d1 % 36524
        n4   = quotient(d2, 1461)
        d3   = d2 % 1461
        n1   = quotient(d3, 365)
        year = (400 * n400) + (100 * n100) + (4 * n4) + n1
        return year if n100 == 4 or n1 == 4 else year + 1

    @classmethod
    def new_year(cls, year):
        """Return the ordinal date of January 1 in the year 'year'."""
        return GregorianDate(year, MonthOfYear.JANUARY, 1).toordinal()

    @classmethod
    def year_end(cls, year):
        """Return the ordinal date of December 31 in the year 'year'."""
        return GregorianDate(year, MonthOfYear.DECEMBER, 31).toordinal()

    @classmethod    
    def year_range(cls, year):
        """Return the range of ordinal dates in the year 'g_year'."""
        return [cls.new_year(year), cls.year_end(year)]

    @classmethod    
    def date_difference(cls, gregorian_date1, gregorian_date2):
        """Return the number of days from date 'date1'
        till date 'date2'."""
        return gregorian_date2.toordinal() - gregorian_date1.toordinal()
    
    def day_number(self):
        """Return the day number in the year."""
        return self.date_difference(GregorianDate(self.year - 1, MonthOfYear.DECEMBER, 31), self)
    
    def days_remaining(self):
        """Return the days remaining in the year."""
        return self.date_difference(self, GregorianDate(self.year, MonthOfYear.DECEMBER, 31))
    
    def toordinal_alt(self):
        """Return the ordinal date equivalent.
        Alternative calculation."""
        m = amod(self.month - 2, 12)
        y = self.year + int(math.floor((self.month) + 9 / 12))
        return (self.EPOCH - 1) - 306 + 365 * (y - 1) + int(math.floor((y - 1) / 4)) - int(math.floor((y - 1) / 100)) + int(math.floor((y - 1) / 400)) + int(math.floor((3 * m - 1) / 5)) + 30 * (m - 1) + self.day

    @classmethod    
    def fromordinal_alt(cls, ordinal):
        """Return the date corresponding to ordinal date .
        Alternative calculation."""
        y = cls.to_year(cls.EPOCH - 1 + ordinal + 306)
        prior_days = ordinal - GregorianDate(y - 1, MonthOfYear.MARCH, 1).toordinal()
        month = amod(quotient(5 * prior_days + 2, 153) + 3, 12)
        year  = y - quotient(month + 9, 12)
        day   = ordinal - GregorianDate(year, month, 1).toordinal() + 1
        return GregorianDate(year, month, day)
    
    @classmethod    
    def to_year_alt(cls, ordinal):
        """Return the year corresponding to the ordinal date.
        Alternative calculation."""
        approx = quotient(ordinal - cls.EPOCH + 2, Fraction(146097, 400))
        start  = (cls.EPOCH        +
                  (365 * approx)         +
                  quotient(approx, 4)    +
                  -quotient(approx, 100) +
                  quotient(approx, 400))
        return approx if ordinal < start else approx + 1

    def nth_day_of_week(self, n, day_of_week):
        """Return the ordinal date of n-th day of week.
        If n>0, return the n-th day of week on or after this date.
        If n<0, return the n-th day of week on or before this date.
        If n=0, return raise an error.
        A k-day of 0 means Sunday, 1 means Monday, and so on."""
        if n > 0:
            return 7 * n + day_of_week.before(self.toordinal())
        elif n < 0:
            return 7 * n + day_of_week.after(self.toordinal())
        else:
            raise ValueError("No valid answer where 'n' == 0.")

    def first_day_of_week(self, day_of_week):
        """Return the ordinal date of first day of week on or after this date."""
        return self.nth_day_of_week(1, day_of_week)
    
    def last_day_of_week(self, day_of_week):
        """Return the ordinal date of last day of week on or before this date."""
        return self.nth_day_of_week(-1, day_of_week)

    @classmethod
    def easter(cls, year):
        """Return ordinal date of Easter in Gregorian year 'year'."""
        century = quotient(year, 100) + 1
        shifted_epact = ((14 + 11 * (year % 19) - int(math.floor((3 * century) / 4)) + int(math.floor((5 + (8 * century)) / 25)) ) % 30)
        adjusted_epact = shifted_epact + 1 if shifted_epact == 0 or (shifted_epact == 1 and 10 < year % 19) else shifted_epact
        apr19 = GregorianDate(year, MonthOfYear.APRIL, 19)
        paschal_moon = apr19.toordinal() - adjusted_epact
        return after_weekday(paschal_moon, DayOfWeek.SUNDAY)

def alt_orthodox_easter(year):
    """Return ordinal date of Orthodox Easter in Gregorian year g_year.
    Alternative calculation."""
    paschal_moon = (354 * year +
                    30 * quotient((7 * year) + 8, 19) +
                    quotient(year, 4)  -
                    quotient(year, 19) -
                    273 +
                    GregorianDate.EPOCH)
    return after_weekday(paschal_moon, DayOfWeek.SUNDAY)

def pentecost(year):
    """Return ordinal date of Pentecost in Gregorian year g_year."""
    return GregorianDate.easter(year) + 49

def labor_day(year):
    """Return the ordinal date of United States Labor Day in Gregorian
    year 'g_year' (the first Monday in September)."""
    return GregorianDate(year, MonthOfYear.SEPTEMBER, 1).first_day_of_week(DayOfWeek.MONDAY)

def memorial_day(year):
    """Return the ordinal date of United States' Memorial Day in Gregorian
    year 'year' (the last Monday in May)."""
    return GregorianDate(year, MonthOfYear.MAY, 31).last_day_of_week(DayOfWeek.MONDAY)

def election_day(year):
    """Return the ordinal date of United States' Election Day in Gregorian
    year 'year' (the Tuesday after the first Monday in November)."""
    return GregorianDate(year, MonthOfYear.NOVEMBER, 2).first_day_of_week(DayOfWeek.TUESDAY)

def daylight_saving_start(year):
    """Return the ordinal date of the start of United States daylight
    saving time in Gregorian year 'year' (the second Sunday in March)."""
    return GregorianDate(year, MonthOfYear.MARCH, 1).nth_day_of_week(2, DayOfWeek.SUNDAY)

def daylight_saving_end(year):
    """Return the ordinal date of the end of United States daylight saving
    time in Gregorian year 'year' (the first Sunday in November)."""
    return GregorianDate(year, MonthOfYear.NOVEMBER, 1).first_day_of_week(DayOfWeek.SUNDAY)

def christmas(year):
    """Return the ordinal date of Christmas in Gregorian year 'year'."""
    return GregorianDate(year, MonthOfYear.DECEMBER, 25).toordinal()

@classmethod    
def advent(year):
    """Return the ordinal date of Advent in Gregorian year 'year'
    (the Sunday closest to November 30)."""
    return  nearest_weekday(GregorianDate(year, MonthOfYear.NOVEMBER, 30).toordinal(), DayOfWeek.SUNDAY)

def epiphany(year):
    """Return the ordinal date of Epiphany in U.S. in Gregorian year 'year'
    (the first Sunday after January 1)."""
    return GregorianDate(year, MonthOfYear.JANUARY, 2).first_day_of_week(DayOfWeek.SUNDAY)

def epiphany_it(year):
    """Return ordinal date of Epiphany in Italy in Gregorian year 'year'."""
    return GregorianDate(year, MonthOfYear.JANUARY, 6)

def unlucky_fridays_in_range(first_ordinal_date, last_ordinal_date):
    """Return the list of Fridays within range 'range' of ordinal dates that
    are day 13 of the relevant Gregorian months."""
    fri  = on_or_after_weekday(first_ordinal_date, DayOfWeek.FRIDAY)
    date = GregorianDate.fromordinal(fri)
    ell  = [fri] if (date.day == 13) else []
    
    if first_ordinal_date <= fri <= last_ordinal_date:
        ell[:0] = unlucky_fridays_in_range(fri + 1, last_ordinal_date)
        return ell
    else:
        return []