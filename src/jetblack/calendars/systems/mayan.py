import math
from jetblack.calendars.utils import amod
from jetblack.calendars.systems.julian import JulianDay
from jetblack.calendars.utils import reduce_cond

class MayanLongCountDate(object):

    EPOCH = JulianDay(584283).toordinal()
    
    def __init__(self, baktun, katun, tun, uinal, kin):
        self.baktun = baktun
        self.katun = katun
        self.tun = tun
        self.uinal = uinal
        self.kin = kin
    
    def to_tuple(self):
        return (self.baktun, self.katun, self.tun, self.uinal, self.kin)
    
    def toordinal(self):
        """Return ordinal date corresponding to the Mayan long count count,
        which is a list [baktun, katun, tun, uinal, kin]."""
        return (self.EPOCH       +
                (self.baktun * 144000) +
                (self.katun * 7200)    +
                (self.tun * 360)       +
                (self.uinal * 20)      +
                self.kin)
    
    @classmethod
    def fromordinal(cls, ordinal):
        """Return Mayan long count date of ordinal date ordinal."""
        long_count = ordinal - cls.EPOCH
        baktun, day_of_baktun  = divmod(long_count, 144000)
        katun, day_of_katun    = divmod(day_of_baktun, 7200)
        tun, day_of_tun        = divmod(day_of_katun, 360)
        uinal, kin             = divmod(day_of_tun, 20)
        return MayanLongCountDate(baktun, katun, tun, uinal, kin)
    
    def __eq__(self, other):
        return isinstance(other, MayanLongCountDate) and all(map(lambda (x,y): x == y, zip(self.to_tuple(), other.to_tuple())))
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __lt__(self, other):
        return isinstance(other, MayanLongCountDate) and reduce_cond(lambda _, (x, y): x < y, lambda r, (x, y): not r and x == y, zip(self.to_tuple(), other.to_tuple()), False)
    
    def __le__(self, other):
        return isinstance(other, MayanLongCountDate) and reduce_cond(lambda _, (x, y): x <= y, lambda r, (x, y): not r and x == y, zip(self.to_tuple(), other.to_tuple()), False)
    
    def __gt__(self, other):
        return isinstance(other, MayanLongCountDate) and reduce_cond(lambda _, (x, y): x > y, lambda r, (x, y): not r and x == y, zip(self.to_tuple(), other.to_tuple()), False)
    
    def __ge__(self, other):
        return isinstance(other, MayanLongCountDate) and reduce_cond(lambda _, (x, y): x >= y, lambda r, (x, y): not r and x == y, zip(self.to_tuple(), other.to_tuple()), False)

class MayanHaabOrdinal(object):

    def __init__(self, month, day):
        self.month = month
        self.day = day
        
    def toordinal(self):
        """Return the number of days into cycle of Mayan haab date h_date."""
        return ((self.month - 1) * 20) + self.day
    
    def to_tuple(self):
        return (self.month, self.day)

    def __eq__(self, other):
        return isinstance(other, MayanHaabOrdinal) and all(map(lambda (x,y): x == y, zip(self.to_tuple(), other.to_tuple())))
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __lt__(self, other):
        return isinstance(other, MayanHaabOrdinal) and reduce_cond(lambda _, (x, y): x < y, lambda r, (x, y): not r and x == y, zip(self.to_tuple(), other.to_tuple()), False)
    
    def __le__(self, other):
        return isinstance(other, MayanHaabOrdinal) and reduce_cond(lambda _, (x, y): x <= y, lambda r, (x, y): not r and x == y, zip(self.to_tuple(), other.to_tuple()), False)
    
    def __gt__(self, other):
        return isinstance(other, MayanHaabOrdinal) and reduce_cond(lambda _, (x, y): x > y, lambda r, (x, y): not r and x == y, zip(self.to_tuple(), other.to_tuple()), False)
    
    def __ge__(self, other):
        return isinstance(other, MayanHaabOrdinal) and reduce_cond(lambda _, (x, y): x >= y, lambda r, (x, y): not r and x == y, zip(self.to_tuple(), other.to_tuple()), False)

class MayanHaabDate(MayanHaabOrdinal):

    EPOCH = MayanLongCountDate.EPOCH - MayanHaabOrdinal(18, 8).toordinal()
    
    def __init__(self, month, day):
        MayanHaabOrdinal.__init__(self, month, day)
    
    @classmethod
    def fromordinal(cls, ordinal):
        """Return Mayan haab date of ordinal date ordinal."""
        count = (ordinal - cls.EPOCH) % 365
        day   = count % 20
        month = int(math.floor(count / 20)) + 1
        return MayanHaabDate(month, day)
    
    def on_or_before(self, ordinal):
        """Return ordinal date of latest date on or before ordinal date date
        that is Mayan haab date haab."""
        return ordinal - ((ordinal - self.EPOCH - self.toordinal()) % 365)

class MayanTzolkinOrdinal(object):

    def __init__(self, number, name):
        self.number = number
        self.name = name

    def to_ordinal(self):
        """Return number of days into Mayan tzolkin cycle of t_date."""
        return (self.number - 1 + (39 * (self.number - self.name))) % 260

    def to_tuple(self):
        return (self.number, self.name)

    def __eq__(self, other):
        return isinstance(other, MayanTzolkinOrdinal) and all(map(lambda (x,y): x == y, zip(self.to_tuple(), other.to_tuple())))
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __lt__(self, other):
        return isinstance(other, MayanTzolkinOrdinal) and reduce_cond(lambda _, (x, y): x < y, lambda r, (x, y): not r and x == y, zip(self.to_tuple(), other.to_tuple()), False)
    
    def __le__(self, other):
        return isinstance(other, MayanTzolkinOrdinal) and reduce_cond(lambda _, (x, y): x <= y, lambda r, (x, y): not r and x == y, zip(self.to_tuple(), other.to_tuple()), False)
    
    def __gt__(self, other):
        return isinstance(other, MayanTzolkinOrdinal) and reduce_cond(lambda _, (x, y): x > y, lambda r, (x, y): not r and x == y, zip(self.to_tuple(), other.to_tuple()), False)
    
    def __ge__(self, other):
        return isinstance(other, MayanTzolkinOrdinal) and reduce_cond(lambda _, (x, y): x >= y, lambda r, (x, y): not r and x == y, zip(self.to_tuple(), other.to_tuple()), False)
    
class MayanTzolkinDate(MayanTzolkinOrdinal):

    EPOCH = MayanLongCountDate.EPOCH - MayanTzolkinOrdinal(4, 20).toordinal()
    
    def __init__(self, number, name):
        MayanTzolkinOrdinal.__init__(self, number, name)
    
    @classmethod
    def fromordinal(cls, date):
        """Return Mayan tzolkin date of ordinal date ordinal."""
        count  = date - cls.EPOCH + 1
        number = amod(count, 13)
        name   = amod(count, 20)
        return MayanTzolkinDate(number, name)
    
    def on_or_before(self, ordinal):
        """Return ordinal date of latest date on or before ordinal date ordinal
        that is Mayan tzolkin date tzolkin."""
        return ordinal - ((ordinal - self.EPOCH - self.toordinal()) % 260)

    @classmethod
    def mayan_year_bearer_from_fixed(cls, date):
        """Return year bearer of year containing fixed date date.
        Raises ValueError for uayeb."""
        x = MayanHaabDate(1, 0).on_or_before(date + 364)
        if MayanHaabDate.from_fixed(date).month == 19:
            raise ValueError("Invalid date")
        return cls.from_fixed(x).name

    @classmethod    
    def mayan_calendar_round_on_or_before(cls, haab, tzolkin, ordinal):
        """Return fixed date of latest date on or before date, that is
        Mayan haab date haab and tzolkin date tzolkin.
        Raises ValueError for impossible combinations."""
        haab_count = haab.toordinal() + MayanHaabDate.EPOCH
        tzolkin_count = tzolkin.toordinal() + MayanTzolkinDate.EPOCH
        diff = tzolkin_count - haab_count
        if diff % 5 == 0:
            return ordinal - ((ordinal - haab_count(365 * diff)) % 18980)
        else:
            raise ValueError("impossible combinination")
