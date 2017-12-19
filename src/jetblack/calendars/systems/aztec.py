import math
from jetblack.calendars.utils import amod, reduce_cond
from jetblack.calendars.datemath import MonthOfYear
from jetblack.calendars.systems.julian import JulianDate

AZTEC_CORRELATION = JulianDate(1521, MonthOfYear.AUGUST, 13).toordinal()

class AztecXihuitlOrdinal(object):

    def __init__(self, month, day):
        self.month = month
        self.day = day 
        
    def toordinal(self):
        """Return the number of elapsed days into cycle of Aztec xihuitl
        date x_date."""
        return  ((self.month - 1) * 20) + self.day - 1

    def to_tuple(self):
        return (self.month, self.day)
    
    def __eq__(self, other):
        return isinstance(other, AztecXihuitlOrdinal) and all(map(lambda (x,y): x == y, zip(self.to_tuple(), other.to_tuple())))
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __lt__(self, other):
        return isinstance(other, AztecXihuitlOrdinal) and reduce_cond(lambda _, (x, y): x < y, lambda r, (x, y): not r and x == y, zip(self.to_tuple(), other.to_tuple()), False)
    
    def __le__(self, other):
        return isinstance(other, AztecXihuitlOrdinal) and reduce_cond(lambda _, (x, y): x <= y, lambda r, (x, y): not r and x == y, zip(self.to_tuple(), other.to_tuple()), False)
    
    def __gt__(self, other):
        return isinstance(other, AztecXihuitlOrdinal) and reduce_cond(lambda _, (x, y): x > y, lambda r, (x, y): not r and x == y, zip(self.to_tuple(), other.to_tuple()), False)
    
    def __ge__(self, other):
        return isinstance(other, AztecXihuitlOrdinal) and reduce_cond(lambda _, (x, y): x >= y, lambda r, (x, y): not r and x == y, zip(self.to_tuple(), other.to_tuple()), False)

class AztecXihuitlDate(AztecXihuitlOrdinal):

    CORRELATION = AZTEC_CORRELATION - AztecXihuitlOrdinal(11, 2).to_ordinal()
    
    def __init__(self, month, day):
        super().__init__(month, day)
        
    @classmethod
    def fromordinal(cls, ordinal):
        """Return Aztec xihuitl date of ordinal date."""
        count = (ordinal - cls.CORRELATION) % 365
        day   = count % 20 + 1
        month = int(math.floor(count / 20)) + 1
        return AztecXihuitlDate(month, day)
    
    # see lines 2239-2246 in calendrica-3.0.cl
    def on_or_before(self, ordinal):
        """Return ordinal date of latest date on or before ordinal date
        that is Aztec xihuitl date xihuitl."""
        return ordinal - (ordinal - self.CORRELATION - self.to_ordinal()) % 365

class AztecTonalpohuallOrdinal(object):
    
    def __init__(self, number, name):
        self.number = number
        self.name = name

    def toordinal(self):
        """Return the number of days into Aztec tonalpohualli cycle of t_date."""
        return (self.number - 1 + 39 * (self.number - self.name)) % 260
    
    def to_tuple(self):
        return (self.number, self.name)
    
    def __eq__(self, other):
        return isinstance(other, AztecXihuitlOrdinal) and all(map(lambda (x,y): x == y, zip(self.to_tuple(), other.to_tuple())))
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __lt__(self, other):
        return isinstance(other, AztecXihuitlOrdinal) and reduce_cond(lambda _, (x, y): x < y, lambda r, (x, y): not r and x == y, zip(self.to_tuple(), other.to_tuple()), False)
    
    def __le__(self, other):
        return isinstance(other, AztecXihuitlOrdinal) and reduce_cond(lambda _, (x, y): x <= y, lambda r, (x, y): not r and x == y, zip(self.to_tuple(), other.to_tuple()), False)
    
    def __gt__(self, other):
        return isinstance(other, AztecXihuitlOrdinal) and reduce_cond(lambda _, (x, y): x > y, lambda r, (x, y): not r and x == y, zip(self.to_tuple(), other.to_tuple()), False)
    
    def __ge__(self, other):
        return isinstance(other, AztecXihuitlOrdinal) and reduce_cond(lambda _, (x, y): x >= y, lambda r, (x, y): not r and x == y, zip(self.to_tuple(), other.to_tuple()), False)

class AztecTonalpohualliDate(AztecTonalpohuallOrdinal):

    CORRELATION = AZTEC_CORRELATION - AztecTonalpohuallOrdinal(1, 5).to_ordinal()
    
    def __init__(self, number, name):
        super().__init__(number, name)

    @classmethod
    def fromordinal(cls, ordinal):
        """Return Aztec tonalpohualli date of ordinal date."""
        count  = ordinal - cls.CORRELATION + 1
        number = amod(count, 13)
        name   = amod(count, 20)
        return AztecTonalpohualliDate(number, name)

    def on_or_before(self, ordinal):
        """Return ordinal date of latest date on or before ordinal date
        that is Aztec tonalpohualli date tonalpohualli."""
        return ordinal - (ordinal - self.CORRELATION - self.to_ordinal()) % 260

class AztecXiuhmolpilliDesignation(AztecTonalpohualliDate):
    
    def __init__(self, number, name):
        super().__init__(number, name)

    @classmethod    
    def fromordinal(cls, ordinal):
        """Return designation of year containing ordinal ordinal.
        Raises ValueError for nemontemi."""
        x = AztecXihuitlDate(18, 20).on_or_before(ordinal + 364)
        month = AztecXihuitlDate.fromordinal(ordinal).month
        if month == 19:
            raise ValueError("nemontemi")
        return AztecTonalpohualliDate.fromordinal(x)

    @classmethod
    def aztec_xihuitl_tonalpohualli_on_or_before(cls, xihuitl, tonalpohualli, ordinal):
        """Return ordinal date of latest xihuitl_tonalpohualli combination
        on or before date date.  That is the date on or before
        date date that is Aztec xihuitl date xihuitl and
        tonalpohualli date tonalpohualli.
        Raises ValueError for impossible combinations."""
        xihuitl_count = xihuitl.to_ordinal() + AztecXihuitlDate.CORRELATION
        tonalpohualli_count = (tonalpohualli.to_ordinal() + AztecTonalpohualliDate.CORRELATION)
        diff = tonalpohualli_count - xihuitl_count
        if diff % 5 == 0:
            return ordinal - (ordinal - xihuitl_count - (365 * diff)) % 18980
        else:
            raise ValueError("impossible combination")
        