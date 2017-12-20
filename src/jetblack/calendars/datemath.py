import math
from enum import IntEnum
from datetime import date, datetime, timedelta

class DayOfWeek(IntEnum):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6
    
class MonthOfYear(IntEnum):
    JANUARY = 1
    FEBRUARY = 2
    MARCH = 3
    APRIL = 4
    MAY = 5
    JUNE = 6
    JULY = 7
    AUGUST = 8
    SEPTEMBER = 9
    OCTOBER = 10
    NOVEMBER = 11
    DECEMBER = 12
    
class BusinessDayConvention(IntEnum):
    NONE = 0
    NEAREST = 1
    PRECEDING = 2
    FOLLOWING = 3
    MODIFIED_PRECEDING = 4
    MODIFIED_FOLLOWING = 5
    
class TimeUnit(IntEnum):
    DAYS = 0
    WEEKS = 1
    MONTHS = 2
    YEARS = 3
    
class Season(IntEnum):
    SPRING = 0
    SUMMER = 90
    AUTUMN = 180
    WINTER = 270
    
def weekday_fromordinal(ordinal):
    """Return day of the week from a fixed date 'date'."""
    return DayOfWeek((ordinal - 1) % 7)

def on_or_before_weekday(ordinal, weekday):
    """Return the ordinal date of the k-day on or before ordinal date 'ordinal'.
    k=0 means Sunday, k=1 means Monday, and so on."""
    return ordinal - weekday_fromordinal(ordinal - weekday)

def on_or_after_weekday(ordinal, weekday):
    """Return the ordinal date of the k-day on or after fixed date 'fixed_date'.
    k=0 means Sunday, k=1 means Monday, and so on."""
    return on_or_before_weekday(ordinal + 6, weekday)

def nearest_weekday(ordinal, weekday):
    """Return the ordinal date of the k-day nearest fixed date 'fixed_date'.
    k=0 means Sunday, k=1 means Monday, and so on."""
    return on_or_before_weekday(ordinal + 3, weekday)

def after_weekday(ordinal, weekday):
    """Return the ordinal date of the k-day after fixed date 'fixed_date'.
    k=0 means Sunday, k=1 means Monday, and so on."""
    return on_or_before_weekday(ordinal + 7, weekday)

def before_weekday(ordinal, weekday):
    """Return the ordinal date of the k-day before fixed date 'date'.
    k=0 means Sunday, k=1 means Monday, and so on."""
    return on_or_before_weekday(ordinal - 1, weekday)

__month_days = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)

class AbstractCalendar(object):

    def isWeekend(self, target_date):
        raise NotImplementedError()
    
    def isHoliday(self, target_date):
        raise NotImplementedError()
    
    def isBusinessDay(self, target_date):
        raise NotImplementedError()

class AbstractWeekendCalendar(AbstractCalendar):

    def __init__(self, weekends):
        self.weekends = weekends
    
    def isWeekend(self, target_date):
        return target_date.weekday() in self.weekends
    
    def isBusinessDay(self, target_date):
        return not (self.isWeekend(target_date) or self.isHoliday(target_date))
        
class SimpleCalendar(AbstractWeekendCalendar):
    
    def __init__(self, weekends=[DayOfWeek.SATURDAY, DayOfWeek.SUNDAY], holidays=[]):
        super().__init__(weekends)
        self.holidays = holidays
    
    def isHoliday(self, target_date):
        return target_date in self.holidays
    
class YearlyCalendar(AbstractWeekendCalendar):
    
    def __init__(self, weekends=[DayOfWeek.SATURDAY, DayOfWeek.SUNDAY]):
        super().__init__(weekends)
        self._holidays = {}
    
    def isHoliday(self, target_date):
        if target_date.year not in self._holidays:
            self._holidays[target_date.year] = self.fetchHolidays(target_date.year)
            
        return target_date in self._holidays[target_date.year]
    
    def fetchHolidays(self, year):
        raise NotImplementedError()
    
WEEKEND_CALENDAR = SimpleCalendar([DayOfWeek.SATURDAY, DayOfWeek.SUNDAY])

def isLeapYear(year):
    """
    Returns true if the year is a leap year.
    
    :param year: The year to check
    :type year: int
    :returns: True if the year is a leap year.
    :rtype: bool
    """
    return ((year % 4 == 0) and ((year % 100 != 0) or (year % 400 == 0)))

def daysInMonth(year, month):
    """
    Returns the number of days in the month.
    """
    return 29 if isLeapYear(year) and month == 2 else __month_days[month - 1] 

def daysInYear(year):
    """
    Returns the number of days in the year.
    """
    return 366 if isLeapYear(year) else 365

def isEndOfMonth(target_date):
    """
    Returns true if the given date is the last day of the month.
    """
    return target_date.day == daysInMonth(target_date.year, target_date.month)

def addMonths(target_date, months, end_of_month = False):
    """
    Adds months to the date. If the end of month anchor is true, keep to the end of 
    the month is the given date was at the end of the month.
    """
    
    if months == 0:
        return target_date
    
    month = target_date.month + months;
    year = target_date.year

    if months > 0:
        year += month // 12
        month = month % 12
    else:
        if month <= 0:
            year += -month // 12 - 1
            month %= 12

    days_in_month = daysInMonth(year, month)

    if end_of_month and isEndOfMonth(target_date):
        return date(year, month, days_in_month)
    else:
        return date(year, month, min(target_date.day, days_in_month))

def nearestBusinessDay(target_date, prefer_forward = True, cal=WEEKEND_CALENDAR):
    """
    Find the nearest business day to a given date.
    """
    if cal.isBusinessDay(target_date):
        return target_date
    
    one_day = timedelta(1)
    forward_date = target_date + one_day
    backward_date = target_date - one_day
    
    while True:
        is_forward_ok = cal.isBusinessDay(forward_date)
        is_backward_ok = cal.isBusinessDay(backward_date)
        if is_forward_ok and (prefer_forward or not is_backward_ok):
            return forward_date
        elif is_backward_ok:
            return backward_date
        forward_date += one_day
        backward_date -= one_day

def addBusinessDays(target_date, count, cal=WEEKEND_CALENDAR):
    """
    Adds business days to a date.
    """
    
    sign = 1 if count > 0 else -1
    signed_day = timedelta(sign)
    
    while count != 0:
        target_date += signed_day
        count -= sign
        
        while not cal.isBusinessDay(target_date):
            target_date += signed_day
    
    return target_date

def adjust(target_date, convention = BusinessDayConvention.FOLLOWING, prefer_forward=True, cal=WEEKEND_CALENDAR):
    
    """
    Adjusts a non-business day to the appropriate near business day
    with respect to the given convention.
    """
    
    if convention == BusinessDayConvention.NONE or cal.isBusinessDay(target_date):
        return target_date
    elif convention == BusinessDayConvention.NEAREST:
        return nearestBusinessDay(target_date, prefer_forward, cal)
    elif convention == BusinessDayConvention.FOLLOWING:
        return addBusinessDays(target_date, 1)
    elif convention == BusinessDayConvention.PRECEDING:
        return addBusinessDays(target_date, -1)
    elif convention == BusinessDayConvention.MODIFIED_FOLLOWING:
        adjusted_date = addBusinessDays(target_date, 1)
        
        if adjusted_date.month == target_date.month:
            return adjusted_date
        else:
            return addBusinessDays(target_date, -1)
    elif convention == BusinessDayConvention.MODIFIED_PRECEDING:
        adjusted_date = addBusinessDays(target_date, -1)
        
        if adjusted_date.month == target_date.month:
            return adjusted_date
        else:
            return addBusinessDays(target_date, 1)
    else:
        raise ValueError("Invalid business day convention")

def advance(target_date, count, unit, convention = BusinessDayConvention.FOLLOWING, end_of_month = False, cal=WEEKEND_CALENDAR):
    
    """
    Advances the given date of the given number of business days and
    returns the result.
    Note: The input date is not modified.
    """
        
    if count == 0:
        return adjust(target_date, convention, cal)
    elif unit == TimeUnit.DAYS:
        return addBusinessDays(target_date, count, cal)
    elif unit == TimeUnit.WEEKS:
        return adjust(target_date + timedelta(days=7*count), convention)
    elif unit == TimeUnit.MONTHS:
        return adjust(addMonths(target_date, count, end_of_month), convention, cal)
    elif unit == TimeUnit.YEARS:
        return adjust(addMonths(target_date, 12*count, end_of_month), convention, cal)
    else:
        raise ValueError("Unhandled TimeUnit")
    
def endOfMonth(year, month):
    """
    Return the date at the last day of the month.
    """
    return date(year, month, daysInMonth(year, month))

def addNthDayOfWeek(target_date, nth, dow, strictly_different):
    """
    Add or subtract a number of different days of the week.
    
    If the start date lies on the specified day of the week and the strictly different flag is false, the current date would be considered the first day of the week.
    """

    if nth == 0:
        return target_date

    if dow < DayOfWeek.MONDAY or dow > DayOfWeek.FRIDAY:
        return target_date

    diff = dow - target_date.weekday()

    if diff == 0 and strictly_different:
        nth += 1 if nth >= 0 else -1

    # forwards
    if nth > 0:
        # If diff = 0 below, the input date is the 1st DOW already, no adjustment 
        # is required. The 'diff' is the adjustment from the input date 
        # required to get to the first DOW matching the 'dow_index' given.

        if diff < 0:
            diff += 7

        adjusted_start_date = target_date + timedelta(diff)
        end_date = adjusted_start_date + timedelta((nth - 1) * 7)
        return end_date
    # backwards
    else:
        # If diff = 0 below, the input date is the 1st DOW already, no adjustment 
        # is required. The 'diff' is the adjustment from the input date 
        # required to get to the first DOW matching the 'dow_index' given.

        if diff > 0:
            diff -= 7

        adjusted_start_date = target_date + timedelta(diff)
        end_date = adjusted_start_date + timedelta((nth + 1) * 7)
        return end_date

def easter(year):
    """
    The date for Easter Sunday for the given year.
    """
    # Note: Only true for Gregorian dates

    y = year
    g = (y - ((y // 19) * 19)) + 1
    c = (y // 100) + 1
    x = ((3 * c) // 4) - 12
    z = (((8 * c) + 5) // 25) - 5
    d = ((5 * y) // 4) - x - 10
    e1 = (11 * g) + 20 + z - x
    e = e1 - ((e1 // 30) * 30)

    # The value of 'e' may be negative. The case of year = 14250, e.g.,
    # produces values of g = 1, z = 40 and x = 95. The value of e1 is thus
    # -24, and the 'mod' code fails to return the proper positive result.
    # The following correction produces a positive value, mod 30, for 'e'.
      
    while e < 0:
        e += 30
   
    if ((e == 25) and (g > 11)) or (e == 24):
        e += 1;

    n = 44 - e;

    if n < 21:
        n += 30
  
    dpn = d + n
    n1 = dpn - ((dpn // 7) * 7)   
    n = n + 7 - n1;

    if n > 31:
        month = 4;
        day = n - 31;
    else:
        month = 3;
        day = n;
   
    return date(year, month, day)

def daysAndMonthsBetween(start_date, end_date):
    """
    Calculates the number of days an months between two dates.
    """
    if start_date == end_date:
        return (0, 0)

    start_date1 = date(start_date.year, start_date.month, 1)
    end_date1 = date(end_date.year, end_date.month, 1)
    months = (end_date1.year - start_date1.year) * 12 + (end_date1.month - start_date1.month)

    if not isEndOfMonth(end_date) and (isEndOfMonth(start_date) or start_date.day > end_date.day):
        --months;

    if start_date.day == end_date.day or (isEndOfMonth(start_date) and isEndOfMonth(end_date)):
        days = 0
    elif start_date.day < end_date.day:
        days = end_date.day - start_date.day
    else:
        days = daysInMonth(start_date.year, start_date.month) - start_date.day + end_date.day

    return (days, months)

def areInSameQuarter(first, second):
    """
    Find out if two dates are in the same quarter.
    """
    if first > second:
        return areInSameQuarter(second, first)

    return first == second or (first.year == second.year and second.month - first.month < 4 and (second.month - 1) % 3 > (first.month - 1) % 3)

def quarterOfYear(target_date):
    """
    Find the quarter of the year for a given date.
    """
    if target_date.month in [MonthOfYear.JANUARY, MonthOfYear.FEBRUARY, MonthOfYear.MARCH]:
        return 1
    elif target_date.month in [MonthOfYear.APRIL, MonthOfYear.MAY, MonthOfYear.JUNE]:
        return 2
    elif target_date.month in [MonthOfYear.JULY, MonthOfYear.AUGUST, MonthOfYear.SEPTEMBER]:
        return 3
    else:
        return 4
    
def weekOfYear(target_date, iso=True):
    """
    Return the week of the year
    """
    return target_date.isocalendar()[1] if iso else 1 + (target_date - date(target_date.year, 1, 1)).days // 7

def equinox(year, season):
    """
    Calculate and Display a single event for a single year (Either a Equiniox or Solstice).
    
    Meeus Astronmical Algorithms Chapter 27
    """
    estimate = estimateEquinox(year, season) # Initial estimate of date of event
    t = (estimate - 2451545.0) / 36525
    w = 35999.373 * t - 2.47
    dL = 1 + 0.0334 * cosFromDeg(w) + 0.0007 * cosFromDeg(2 * w)
    s = periodic24(t)
    julianEmphemerisDays = estimate + ((0.00001 * s) / dL)
    tdt = fromJDtoUtc(julianEmphemerisDays)
    return fromTdTtoUtc(tdt)

def estimateEquinox(year, season):
    """
    Calculate an initial guess as the Julian Date of the Equinox or Solstice of a Given Year.
    
    Meeus Astronmical Algorithms Chapter 27
    """
    # Valid for years 1000 to 3000
    y = (year - 2000) / 1000.0;
    if season == Season.SPRING:
        return 2451623.80984 + 365242.37404 * y + 0.05169 * (y * y) - 0.00411 * (y * y * y) - 0.00057 * (y * y * y * y)
    elif season == season.SUMMER:
        return 2451716.56767 + 365241.62603 * y + 0.00325 * (y * y) + 0.00888 * (y * y * y) - 0.00030 * (y * y * y * y)
    elif season == Season.AUTUMN:
        return 2451810.21715 + 365242.01767 * y - 0.11575 * (y * y) + 0.00337 * (y * y * y) + 0.00078 * (y * y * y * y)
    elif season == Season.WINTER:
        return 2451900.05952 + 365242.74049 * y - 0.06223 * (y * y) - 0.00823 * (y * y * y) + 0.00032 * (y * y * y * y)
    else:
        raise ValueError("Unknown season")
    
def periodic24(T):
    """
    Calculate 24 Periodic Terms
    
    Meeus Astronmical Algorithms Chapter 27
    """
    a = [
        485, 203, 199, 182, 156, 136,
        77, 74, 70, 58, 52, 50,
        45, 44, 29, 18, 17, 16,
        14, 12, 12, 12, 9, 8
    ]
    b = [
        324.96, 337.23, 342.08, 27.85, 73.14, 171.52,
        222.54, 296.72, 243.58, 119.81, 297.17, 21.02,
        247.54, 325.15, 60.93, 155.12, 288.79, 198.04,
        199.76, 95.39, 287.11, 320.81, 227.73, 15.45
    ]
    c = [
        1934.136, 32964.467, 20.186, 445267.112, 45036.886, 22518.443,
        65928.934, 3034.906, 9037.513, 33718.147, 150.678, 2281.226,
        29929.562, 31555.956, 4443.417, 67555.328, 4562.452, 62894.029,
        31436.921, 14577.848, 31931.756, 34777.259, 1222.114, 16859.074
    ]

    s = 0.0;
    for i in range(24):
        s += a[i] * cosFromDeg(b[i] + c[i] * T);
    return s;
    
def fromTdTtoUtc(tdt):
    """
    Correct TDT to UTC
    
    Meeus Astronmical Algroithms Chapter 10
    
    tdt: >Date as a Terrestrial Dynamic Time
    """
    
    # Correction lookup table has entry for every even year between TBLfirst and TBLlast
    firstCorrectionYear = 1620
    lastCorrectionYear = 2002
    correctionInSeconds = [
         121, 112, 103, 95, 88, 82, 77, 72, 68, 63, 60, 56, 53, 51, 48, 46, 44, 42, 40, 38, # from 1620
        35, 33, 31, 29, 26, 24, 22, 20, 18, 16, 14, 12, 11, 10, 9, 8, 7, 7, 7, 7, # from 1660  
           7, 7, 8, 8, 9, 9, 9, 9, 9, 10, 10, 10, 10, 10, 10, 10, 10, 11, 11, 11, # from 1700
        11, 11, 12, 12, 12, 12, 13, 13, 13, 14, 14, 14, 14, 15, 15, 15, 15, 15, 16, 16, # from 1740
        16, 16, 16, 16, 16, 16, 15, 15, 14, 13, # from 1780
        13.1, 12.5, 12.2, 12.0, 12.0, 12.0, 12.0, 12.0, 12.0, 11.9, 11.6, 11.0, 10.2, 9.2, 8.2, # from 1800
        7.1, 6.2, 5.6, 5.4, 5.3, 5.4, 5.6, 5.9, 6.2, 6.5, 6.8, 7.1, 7.3, 7.5, 7.6, # from 1830
        7.7, 7.3, 6.2, 5.2, 2.7, 1.4, -1.2, -2.8, -3.8, -4.8, -5.5, -5.3, -5.6, -5.7, -5.9, # from 1860
        -6.0, -6.3, -6.5, -6.2, -4.7, -2.8, -0.1, 2.6, 5.3, 7.7, 10.4, 13.3, 16.0, 18.2, 20.2, # from 1890
        21.1, 22.4, 23.5, 23.8, 24.3, 24.0, 23.9, 23.9, 23.7, 24.0, 24.3, 25.3, 26.2, 27.3, 28.2, # from 1920
        29.1, 30.0, 30.7, 31.4, 32.2, 33.1, 34.0, 35.0, 36.5, 38.3, 40.2, 42.2, 44.5, 46.5, 48.5, # from 1950
        50.5, 52.5, 53.8, 54.9, 55.8, 56.9, 58.3, 60.0, 61.6, 63.0, 63.8, 64.3 # from 1980 to 2002
    ]

    # Values for Delta T for 2000 thru 2002 from NASA
    deltaT = 0 # deltaT = TDT - UTC (in Seconds)
    year = tdt.year
    t = (year - 2000) / 100.0 # Centuries from the epoch 2000.0

    if year >= firstCorrectionYear and year <= lastCorrectionYear:
        # Find correction in table
        if year % 2 != 0:
            # Odd year - interpolate
            deltaT = (correctionInSeconds[(year - firstCorrectionYear - 1) / 2] + correctionInSeconds[(year - firstCorrectionYear + 1) / 2]) / 2
        else:
            # Even year - direct table lookup
            deltaT = correctionInSeconds[(year - firstCorrectionYear) / 2]
    elif year < 948:
        deltaT = 2177 + 497 * t + 44.1 * (t * t)
    elif year >= 948:
        deltaT = 102 + 102 * t + 25.3 * (t * t)
        if year >= 2000 and year <= 2100:
            # Special correction to avoid discontinurity in 2000
            deltaT += 0.37 * (year - 2100);
    else:
        raise ValueError("Error: TDT to UTC correction not computed")
    
    return tdt - timedelta(seconds = deltaT)

def fromJDtoUtc(julianDate):
    """
    Julian Date to UTC Date Object
     
    Meeus Astronmical Algorithms Chapter 7
    """

    z = int(math.floor(julianDate + 0.5)) # Whole Julian Days
    f = (julianDate + 0.5) - z # Fractional Julian Days

    if z < 2299161:
        a = z
    else:
        alpha = int(math.floor((z - 1867216.25) / 36524.25))
        a = z + 1 + alpha - alpha / 4;
    b = a + 1524
    c = int(math.floor((b - 122.1) / 365.25))
    d = int(math.floor(365.25 * c))
    e = int(math.floor((b - d) / 30.6001))
    dayOfMonth = b - d - int(math.floor(30.6001 * e)) + f # Day of Month with decimals for time
    month = e - (1 if e < 13.5 else 13)
    year = c - 4716 if month > 2.5 else 4715
    day = int(math.floor(dayOfMonth))
    h = 24 * (dayOfMonth - day); # Hours and fractional hours 
    hour = int(math.floor(h))
    m = 60 * (h - hour); # Minutes and fractional minutes
    minute = int(math.floor(m))
    second = int(math.floor(60 * (m - minute)))
    return datetime(year, month, day, hour, minute, second)
    
def cosFromDeg(deg):
    return math.cos(deg * math.pi / 180);


if __name__ == "__main__":
    print(weekOfYear(date(2017, 1, 1), True)) # 52
    print(weekOfYear(date(2017, 1, 1), False)) # 1
    print(weekOfYear(date(2017, 6, 1), True)) # 22
    print(weekOfYear(date(2017, 6, 1), False)) # 22
    print(weekOfYear(date(2017, 12, 1), True)) # 48
    print(weekOfYear(date(2017, 12, 1), False)) # 48
    print(weekOfYear(date(2017, 12, 31), True)) # 52
    print(weekOfYear(date(2017, 12, 31), False)) # 53
    