from mpmath import mpf
import math
from jetblack.calendars.systems.gregorian import GregorianDate
from jetblack.calendars.datemath import MonthOfYear, Season
from jetblack.calendars.solar import MEAN_TROPICAL_YEAR, solar_longitude, solar_longitude_after, estimate_prior_solar_longitude
from jetblack.calendars.lunar import MEAN_SYNODIC_MONTH, new_moon_before, new_moon_at_or_after
from jetblack.calendars.location import Location
from jetblack.calendars.timemath import Clock
from jetblack.calendars.utils import next_int, amod
from jetblack.calendars.trigonometry import angle

class ChineseDate(object):

    EPOCH = GregorianDate(-2636, MonthOfYear.FEBRUARY, 15).toordinal()
    
    def __init__(self, cycle, year, month, leap, day):
        self.cycle = cycle
        self.year = year
        self.month = month
        self.leap = leap
        self.day = day
    
    def toordinal(self):
        """Return ordinal date of Chinese date, c_date."""
        mid_year = int(math.floor(self.EPOCH + ((((self.cycle - 1) * 60) + (self.year - 1) + 1/2) * MEAN_TROPICAL_YEAR)))
        new_year = self.new_year_on_or_before(mid_year)
        p = self.new_moon_on_or_after(new_year + ((self.month - 1) * 29))
        d = self.fromordinal(p)
        prior_new_moon = (p if ((self.month == d.month) and (self.leap == d.leap)) else self.new_moon_on_or_after(1 + p))
        return prior_new_moon + self.day - 1

    @classmethod    
    def fromordinal(cls, ordinal):
        """Return Chinese date (cycle year month leap day) of ordinal date, 'ordinal'."""
        s1 = cls.winter_solstice_on_or_before(ordinal)
        s2 = cls.winter_solstice_on_or_before(s1 + 370)
        next_m11 = cls.new_moon_before(1 + s2)
        m12 = cls.new_moon_on_or_after(1 + s1)
        leap_year = int(round((next_m11 - m12) / MEAN_SYNODIC_MONTH)) == 12
    
        m = cls.new_moon_before(1 + ordinal)
        month = amod(int(round((m - m12) / MEAN_SYNODIC_MONTH)) - (1 if (leap_year and cls.is_prior_leap_month(m12, m)) else 0), 12)
        leap_month = (leap_year and cls.is_no_major_solar_term(m) and (not cls.is_prior_leap_month(m12, cls.new_moon_before(m))))
        elapsed_years = (int(math.floor(mpf(1.5) - (month / 12) + ((ordinal - cls.EPOCH) / MEAN_TROPICAL_YEAR))))
        cycle = 1 + int(math.floor((elapsed_years - 1) / 60))
        year = amod(elapsed_years, 60)
        day = 1 + (ordinal - m)
        return ChineseDate(cycle, year, month, leap_month, day)

    @classmethod        
    def location(cls, tee):
        """Return location of Beijing; time zone varies with time, tee."""
        year = GregorianDate.to_year(int(math.floor(tee)))
        if (year < 1929):
            return Location(angle(39, 55, 0), angle(116, 25, 0), 43.5, Clock.days_from_hours(1397/180))
        else:
            return Location(angle(39, 55, 0), angle(116, 25, 0), 43.5, Clock.days_from_hours(8))

    @classmethod
    def solar_longitude_on_or_after(cls, lam, ordinal):
        """Return moment (Beijing time) of the first date on or after
        ordinal date, 'ordinal_date', (Beijing time) when the solar longitude
        will be 'lam' degrees."""
        tee = solar_longitude_after(lam, cls.location(ordinal).universal_from_standard(ordinal))
        return cls.location(tee).standard_from_universal(tee)

    @classmethod
    def major_solar_term(cls, ordinal):
        """Return last Chinese major solar term (zhongqi) before
        ordinal date, 'ordinal'."""
        s = solar_longitude(cls.location(ordinal).universal_from_standard(ordinal))
        return amod(2 + int(math.floor(int(s) / 30)), 12)

    @classmethod
    def major_solar_term_on_or_after(cls, ordinal):
        """Return moment (in Beijing) of the first Chinese major
        solar term (zhongqi) on or after ordinal date, 'ordinal'.  The
        major terms begin when the sun's longitude is a
        multiple of 30 degrees."""
        s = solar_longitude(cls.midnight(ordinal))
        l = (30 * int(math.ceil(s / 30))) % 360
        return cls.solar_longitude_on_or_after(l, ordinal)

    @classmethod    
    def current_minor_solar_term(cls, ordinal):
        """Return last Chinese minor solar term (jieqi) before date, 'ordinal'."""
        s = solar_longitude(cls.location(ordinal).universal_from_standard(ordinal))
        return amod(3 + int(math.floor((s - 15) / 30)), 12)

    @classmethod    
    def minor_solar_term_on_or_after(cls, ordinal):
        """Return moment (in Beijing) of the first Chinese minor solar
        term (jieqi) on or after ordinal date, 'ordinal'.  The minor terms
        begin when the sun's longitude is an odd multiple of 15 degrees."""
        s = solar_longitude(cls.midnight(ordinal))
        l = (30 * int(math.ceil((s - 15) / 30)) + 15) % 360
        return cls.solar_longitude_on_or_after(l, ordinal)

    @classmethod    
    def new_moon_before(cls, ordinal):
        """Return ordinal date (Beijing) of first new moon before ordinal date, 'ordinal'."""
        tee = new_moon_before(cls.midnight(ordinal))
        return int(math.floor(cls.location(tee).standard_from_universal(tee)))
    
    @classmethod    
    def new_moon_on_or_after(cls, ordinal):
        """Return ordinal date (Beijing) of first new moon on or after
        ordinal date, 'ordinal'."""
        tee = new_moon_at_or_after(cls.midnight(ordinal))
        return int(math.floor(cls.location(tee).standard_from_universal(tee)))

    @classmethod    
    def is_no_major_solar_term(cls, ordinal):
        """Return True if Chinese lunar month starting on date, 'ordinal',
        has no major solar term."""
        return cls.major_solar_term(ordinal) == cls.major_solar_term(cls.new_moon_on_or_after(ordinal + 1))

    @classmethod    
    def midnight(cls, ordinal):
        """Return Universal time of (clock) midnight at start of ordinal
        date, 'ordinal', in China."""
        return cls.location(ordinal).universal_from_standard(ordinal)

    @classmethod    
    def winter_solstice_on_or_before(cls, ordinal):
        """Return ordinal date, in the Chinese zone, of winter solstice
        on or before ordinal date, 'ordinal'."""
        midnight_tomorrow = cls.midnight(ordinal + 1)
        approx = estimate_prior_solar_longitude(Season.WINTER, midnight_tomorrow)
        return next_int(int(math.floor(approx)) - 1, lambda day: Season.WINTER < solar_longitude(cls.midnight(1 + day)))
    
    @classmethod    
    def new_year_in_sui(cls, ordinal):
        """Return ordinal date of Chinese New Year in sui (period from
        solstice to solstice) containing date, 'ordinal'."""
        s1 = cls.winter_solstice_on_or_before(ordinal)
        s2 = cls.winter_solstice_on_or_before(s1 + 370)
        next_m11 = cls.new_moon_before(1 + s2)
        m12 = cls.new_moon_on_or_after(1 + s1)
        m13 = cls.new_moon_on_or_after(1 + m12)
        leap_year = int(round((next_m11 - m12) / MEAN_SYNODIC_MONTH)) == 12
    
        if (leap_year and
            (cls.is_no_major_solar_term(m12) or cls.is_no_major_solar_term(m13))):
            return cls.new_moon_on_or_after(1 + m13)
        else:
            return m13

    @classmethod
    def new_year_on_or_before(cls, ordinal):
        """Return ordinal date of Chinese New Year on or before ordinal date, 'ordinal'."""
        new_year = cls.new_year_in_sui(ordinal)
        if (ordinal >= new_year):
            return new_year
        else:
            return cls.new_year_in_sui(ordinal - 180)

    @classmethod    
    def new_year(cls, gregorian_year):
        """Return ordinal date of Chinese New Year in Gregorian year, 'gregorian_year'."""
        july1 = GregorianDate(gregorian_year, MonthOfYear.JULY, 1).toordinal()
        return cls.new_year_on_or_before(july1)

    @classmethod
    def is_prior_leap_month(cls, m_prime, m):
        """Return True if there is a Chinese leap month on or after lunar
        month starting on ordinal day, m_prime and at or before
        lunar month starting at ordinal date, m."""
        return ((m >= m_prime) and
                (cls.is_no_major_solar_term(m) or
                 cls.is_prior_leap_month(m_prime, cls.new_moon_before(m))))

    @classmethod
    def dragon_festival(cls, gregorian_year):
        """Return ordinal date of the Dragon Festival occurring in Gregorian
        year 'gregorian_year'."""
        elapsed_years = 1 + gregorian_year - GregorianDate.to_year(cls.EPOCH)
        cycle = 1 + int(math.floor((elapsed_years - 1) / 60))
        year = amod(elapsed_years, 60)
        return ChineseDate(cycle, year, 5, False, 5).toordinal()

    @classmethod
    def qing_ming(cls, gregorian_year):
        """Return ordinal date of Qingming occurring in Gregorian year, 'gregorian_year'."""
        return int(math.floor(cls.minor_solar_term_on_or_after(GregorianDate(gregorian_year, MonthOfYear.MARCH, 30).toordinal())))

    def age(self, ordinal):
        """Return the age at ordinal date, date, given Chinese birthdate, birthdate,
        according to the Chinese custom.
        Raises ValueError if date is before birthdate."""
        today = self.fromordinal(ordinal)
        if (ordinal >= self.toordinal()):
            return (60 * (today.cycle - self.cycle) + (today.year -  self.year) + 1)
        else:
            raise ValueError("ordinal_date is before birthdate")
    
    @classmethod    
    def year_marriage_augury(cls, cycle, year):
        """Return the marriage augury type of Chinese year, year in cycle, cycle.
        0 means lichun does not occur (widow or double-blind years),
        1 means it occurs once at the end (blind),
        2 means it occurs once at the start (bright), and
        3 means it occurs twice (double-bright or double-happiness)."""
        new_year = ChineseDate(cycle, year, 1, False, 1).toordinal()
        c = (cycle + 1) if (year == 60) else cycle
        y = 1 if (year == 60) else (year + 1)
        next_new_year = ChineseDate(c, y, 1, False, 1).toordinal()
        first_minor_term = cls.current_minor_solar_term(new_year)
        next_first_minor_term = cls.current_minor_solar_term(next_new_year)
        if ((first_minor_term == 1) and (next_first_minor_term == 12)):
            res = 0
        elif ((first_minor_term == 1) and (next_first_minor_term != 12)):
            res = 1
        elif ((first_minor_term != 1) and (next_first_minor_term == 12)):
            res = 2
        else:
            res = 3
        return res

class ChineseName(object):

    MONTH_NAME_EPOCH = 57
    DAY_NAME_EPOCH = 45
    
    def __init__(self, stem, branch):
        if stem % 2 != branch % 2:
            raise ValueError("Combination/branch combination is not possible")
        self.stem = stem
        self.branch = branch
        
    @classmethod
    def sexagesimal_name(n):
        """Return the n_th name of the Chinese sexagesimal cycle."""
        return ChineseName(amod(n, 10), amod(n, 12))

    @classmethod
    def chinese_name_difference(cls, c_name1, c_name2):
        """Return the number of names from Chinese name c_name1 to the
        next occurrence of Chinese name c_name2."""
        stem_difference   = c_name2.stem - c_name1.stem
        branch_difference = c_name2.branch - c_name1.branch
        return 1 + ((stem_difference - 1 + 25 * (branch_difference - stem_difference)) % 60)

    @classmethod
    def year_name(cls, year):
        """Return sexagesimal name for Chinese year, year, of any cycle."""
        return cls.sexagesimal_name(year)

    @classmethod
    def month_name(cls, month, year):
        """Return sexagesimal name for month, month, of Chinese year, year."""
        elapsed_months = (12 * (year - 1)) + (month - 1)
        return cls.sexagesimal_name(elapsed_months - cls.MONTH_NAME_EPOCH)

    @classmethod
    def day_name(cls, date):
        """Return Chinese sexagesimal name for date, date."""
        return cls.sexagesimal_name(date - cls.DAY_NAME_EPOCH)

    @classmethod
    def day_name_on_or_before(cls, name, date):
        """Return ordinal date of latest date on or before ordinal date, date, that
        has Chinese name, name."""
        return date - ((date + cls.name_difference(name, cls.sexagesimal_name(cls.DAY_NAME_EPOCH))) % 60)

def japanese_location(tee):
    """Return the location for Japanese calendar; varies with moment, tee."""
    year = GregorianDate.to_year(int(math.floor(tee)))
    if (year < 1888):
        # Tokyo (139 deg 46 min east) local time
        loc = Location(mpf(35.7), angle(139, 46, 0), 24, Clock.days_from_hours(9 + 143/450))
    else:
        # Longitude 135 time zone
        loc = Location(35, 135, 0, Clock.days_from_hours(9))
    return loc

def korean_location(tee):
    """Return the location for Korean calendar; varies with moment, tee."""
    # Seoul city hall at a varying time zone.
    if (tee < GregorianDate(1908, MonthOfYear.APRIL, 1).toordinal()):
        #local mean time for longitude 126 deg 58 min
        z = 3809/450
    elif (tee < GregorianDate(1912, MonthOfYear.JANUARY, 1).toordinal()):
        z = 8.5
    elif (tee < GregorianDate(1954, MonthOfYear.MARCH, 21).toordinal()):
        z = 9
    elif (tee < GregorianDate(1961, MonthOfYear.AUGUST, 10).toordinal()):
        z = 8.5
    else:
        z = 9
    return Location(angle(37, 34, 0), angle(126, 58, 0), 0, Clock.days_from_hours(z))

def korean_year(cycle, year):
    """Return equivalent Korean year to Chinese cycle, cycle, and year, year."""
    return (60 * cycle) + year - 364

def vietnamese_location(tee):
    """Return the location for Vietnamese calendar is Hanoi;
    varies with moment, tee. Time zone has changed over the years."""
    if (tee < GregorianDate.new_year(1968)):
        z = 8
    else:
        z =7
    return Location(angle(21, 2, 0), angle(105, 51, 0), 12, Clock.days_from_hours(z))