import math
from jetblack.calendars.systems.julian import JulianDay
from jetblack.calendars.systems.gregorian import GregorianDate
from jetblack.calendars.utils import amod, reduce_cond

class BalinesePawukonDate(object):

    EPOCH = JulianDay(146).toordinal()
    
    def __init__(self, luang, dwiwara, triwara, caturwara, pancawara, sadwara, saptawara, asatawara, sangawara, dasawara):
        self.luang = luang
        self.dwiwara = dwiwara
        self.triwara = triwara
        self.caturwara = caturwara
        self.pancawara = pancawara
        self.sadwara = sadwara
        self.saptawara = saptawara
        self.asatawara = asatawara
        self.sangawara = sangawara
        self.dasawara = dasawara
    
    def to_tuple(self):
        return (self.luang, self.dwiwara, self.triwara, self.caturwara, self.pancawara, self.sadwara, self.saptawara, self.asatawara, self.sangawara, self.dasawara)
    
    @classmethod
    def fromordinal(cls, ordinal):
        """Return the positions of date date in ten cycles of Balinese Pawukon
        calendar."""
        return BalinesePawukonDate(cls.luang_fromordinal(ordinal),
                                   cls.dwiwara_fromordinal(ordinal),
                                   cls.triwara_fromordinal(ordinal),
                                   cls.caturwara_fromordinal(ordinal),
                                   cls.pancawara_fromordinal(ordinal),
                                   cls.sadwara_fromordinal(ordinal),
                                   cls.saptawara_fromordinal(ordinal),
                                   cls.asatawara_fromordinal(ordinal),
                                   cls.sangawara_fromordinal(ordinal),
                                   cls.dasawara_fromordinal(ordinal))

    @classmethod
    def day_fromordinal(cls, ordinal):
        """Return the position of date date in 210_day Pawukon cycle."""
        return (ordinal - cls.EPOCH) % 210

    @classmethod
    def luang_fromordinal(cls, ordinal):
        """Check membership of ordinal date in "1_day" Balinese cycle."""
        return cls.dasawara_fromordinal(ordinal) % 2 == 0

    @classmethod
    def dwiwara_fromordinal(cls, ordinal):
        """Return the position of ordinal date in 2_day Balinese cycle."""
        return amod(cls.dasawara_fromordinal(ordinal), 2)
    
    @classmethod
    def triwara_fromordinal(cls, ordinal):
        """Return the position of date date in 3_day Balinese cycle."""
        return (cls.day_fromordinal(ordinal) % 3) + 1
    
    @classmethod
    def caturwara_fromordinal(cls, ordinal):
        """Return the position of ordinal date in 4_day Balinese cycle."""
        return amod(cls.asatawara_fromordinal(ordinal), 4)
    
    @classmethod
    def pancawara_fromordinal(cls, ordinal):
        """Return the position of date date in 5_day Balinese cycle."""
        return amod(cls.day_fromordinal(ordinal) + 2, 5)
    
    @classmethod
    def sadwara_fromordinal(cls, ordinal):
        """Return the position of date date in 6_day Balinese cycle."""
        return (cls.day_fromordinal(ordinal) % 6) + 1
    
    @classmethod
    def saptawara_fromordinal(cls, ordinal):
        """Return the position of date date in Balinese week."""
        return (cls.day_fromordinal(ordinal) % 7) + 1
    
    @classmethod
    def asatawara_fromordinal(cls, ordinal):
        """Return the position of date date in 8_day Balinese cycle."""
        day = cls.day_fromordinal(ordinal)
        return (max(6, 4 + ((day - 70) % 210)) % 8) + 1
    
    @classmethod
    def sangawara_fromordinal(cls, ordinal):
        """Return the position of date date in 9_day Balinese cycle."""
        return (max(0, cls.day_fromordinal(ordinal) - 3) % 9) + 1
    
    @classmethod
    def dasawara_fromordinal(cls, ordinal):
        """Return the position of date date in 10_day Balinese cycle."""
        i = cls.pancawara_fromordinal(ordinal) - 1
        j = cls.saptawara_fromordinal(ordinal) - 1
        return (1 + [5, 9, 7, 4, 8][i] + [5, 4, 3, 7, 8, 6, 9][j]) % 10
    
    @classmethod
    def week_fromordinal(cls, ordinal):
        """Return the  week number of date date in Balinese cycle."""
        return int(math.floor(cls.day_fromordinal(ordinal) / 7)) + 1
    
    def on_or_before(self, ordinal):
        """Return last ordinal date on or before date with Pawukon date b_date."""
        a5 = self.pancawara - 1
        a6 = self.sadwara   - 1
        b7 = self.saptawara - 1
        b35 = (a5 + 14 + (15 * (b7 - a5))) % 35
        days = a6 + (36 * (b35 - a6))
        cap_Delta = self.day_fromordinal(0)
        return ordinal - (ordinal + cap_Delta - days) % 210

    @classmethod    
    def positions_in_range(cls, n, c, cap_Delta, pair):
        """Return the list of occurrences of n-th day of c-day cycle
        in range.
        cap_Delta is the position in cycle of RD 0."""
        a = pair[0]
        b = pair[1]
        pos = a + (n - a - cap_Delta - 1) % c
        return [] if pos > b else [pos].extend(cls.positions_in_range(n, c, cap_Delta, [pos + 1, b]))

    @classmethod    
    def kajeng_keliwon(cls, gregorian_year):
        """Return the occurrences of Kajeng Keliwon (9th day of each
        15_day subcycle of Pawukon) in Gregorian year gregorian_year."""
        year = GregorianDate.year_range(gregorian_year)
        cap_Delta = cls.day_fromordinal(0)
        return cls.positions_in_range(9, 15, cap_Delta, year)
    
    @classmethod    
    def tumpek(cls, gregorian_year):
        """Return the occurrences of Tumpek (14th day of Pawukon and every
        35th subsequent day) within Gregorian year gregorian_year."""
        year = GregorianDate.year_range(gregorian_year)
        cap_Delta = cls.day_fromordinal(0)
        return cls.positions_in_range(14, 35, cap_Delta, year)

    def __eq__(self, other):
        return isinstance(other, BalinesePawukonDate) and all(map(lambda (x,y): x == y, zip(self.to_tuple(), other.to_tuple())))
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __lt__(self, other):
        return isinstance(other, BalinesePawukonDate) and reduce_cond(lambda _, (x, y): x < y, lambda r, (x, y): not r and x == y, zip(self.to_tuple(), other.to_tuple()), False)
    
    def __le__(self, other):
        return isinstance(other, BalinesePawukonDate) and reduce_cond(lambda _, (x, y): x <= y, lambda r, (x, y): not r and x == y, zip(self.to_tuple(), other.to_tuple()), False)
    
    def __gt__(self, other):
        return isinstance(other, BalinesePawukonDate) and reduce_cond(lambda _, (x, y): x > y, lambda r, (x, y): not r and x == y, zip(self.to_tuple(), other.to_tuple()), False)
    
    def __ge__(self, other):
        return isinstance(other, BalinesePawukonDate) and reduce_cond(lambda _, (x, y): x >= y, lambda r, (x, y): not r and x == y, zip(self.to_tuple(), other.to_tuple()), False)