import math
from jetblack.calendars.utils  import amod
from jetblack.calendars.months import MonthOfYear
from jetblack.calendars.systems.gregorian import GregorianDate
from jetblack.calendars.utils import reduce_cond
from jetblack.calendars.weekdays import DayOfWeek, weekday_fromordinal

class IsoDate(object):
    
    def __init__(self, year, week, day):
        self.year = year
        self.week = week
        self.day = day
        
    def toordinal(self):
        """Return the ordinal date equivalent to ISO date 'i_date'."""
        return GregorianDate(self.year - 1, MonthOfYear.DECEMBER, 28).nth_day_of_week(self.week, DayOfWeek.SUNDAY) + self.day
    
    @classmethod
    def fromordinal(cls, ordinal):
        """Return the ISO date corresponding to the ordinal date 'ordinal'."""
        approx = GregorianDate.to_year(ordinal - 3)
        year   = (approx +
                  1 if ordinal >= IsoDate(approx + 1, 1, 1).toordinal()
                  else approx)
        week   = 1 + int(math.floor(ordinal - IsoDate(year, 1, 1).toordinal()/ 7))
        day    = amod(ordinal, 7)
        return IsoDate(year, week, day)

    @classmethod    
    def is_long_year(cls, iso_year):
        """Return True if ISO year 'iso_year' is a long (53-week) year."""
        jan1  = weekday_fromordinal(GregorianDate.new_year(iso_year))
        dec31 = weekday_fromordinal(GregorianDate.year_end(iso_year))
        return jan1 == DayOfWeek.THURSDAY or dec31 == DayOfWeek.THURSDAY

    def to_tuple(self):
        return (self.year, self.week, self.day)
    
    def __eq__(self, other):
        return isinstance(other, IsoDate) and all(map(lambda (x,y): x == y, zip(self.to_tuple(), other.to_tuple())))
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __lt__(self, other):
        return isinstance(other, IsoDate) and reduce_cond(lambda _, (x, y): x < y, lambda r, (x, y): not r and x == y, zip(self.to_tuple(), other.to_tuple()), False)
    
    def __le__(self, other):
        return isinstance(other, IsoDate) and reduce_cond(lambda _, (x, y): x <= y, lambda r, (x, y): not r and x == y, zip(self.to_tuple(), other.to_tuple()), False)
    
    def __gt__(self, other):
        return isinstance(other, IsoDate) and reduce_cond(lambda _, (x, y): x > y, lambda r, (x, y): not r and x == y, zip(self.to_tuple(), other.to_tuple()), False)
    
    def __ge__(self, other):
        return isinstance(other, IsoDate) and reduce_cond(lambda _, (x, y): x >= y, lambda r, (x, y): not r and x == y, zip(self.to_tuple(), other.to_tuple()), False)
    
