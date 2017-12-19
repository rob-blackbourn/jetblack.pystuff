from jetblack.calendars.utils import reduce_cond

def _cmp(x, y):
    return 0 if x == y else 1 if x > y else -1

class YearMonthDay(object):
    
    def __init__(self, year, month, day):
        self._year = year
        self._month = month
        self._day = day
    
    @property
    def year(self):
        """year (1-9999)"""
        return self._year

    @property
    def month(self):
        """month (1-12)"""
        return self._month

    @property
    def day(self):
        """day (1-31)"""
        return self._day
    
    def to_tuple(self):
        return (self.year, self.month, self.day)
    
    def __str__(self):
        return "{0}-{1:02}-{2:02}".format(self.year, self.month, self.day)
    
    def __eq__(self, other):
        return self._cmp(other) == 0

    def __le__(self, other):
        return self._cmp(other) <= 0

    def __lt__(self, other):
        return self._cmp(other) < 0

    def __ge__(self, other):
        return self._cmp(other) >= 0

    def __gt__(self, other):
        return self._cmp(other) > 0

    def _cmp(self, other):
        y, m, d = self._year, self._month, self._day
        y2, m2, d2 = other._year, other._month, other._day
        return _cmp((y, m, d), (y2, m2, d2))
