from datetime import date, timedelta

from jetblack.calendars.weekdays import DayOfWeek
from jetblack.calendars.months import MonthOfYear
from jetblack.calendars.daterules import BusinessDayConvention
from jetblack.calendars.holidays import SimpleCalendar

__month_days = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)

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

def advance(target_date, days=None, weeks=None, months=None, years = None, convention = BusinessDayConvention.FOLLOWING, end_of_month = False, cal=WEEKEND_CALENDAR):
    
    """
    Advances the given date of the given number of business days and
    returns the result.
    Note: The input date is not modified.
    """
        
    if not (days or weeks or months or years):
        return adjust(target_date, convention, cal)
    
    if years:
        target_date = adjust(addMonths(target_date, 12*years, end_of_month), convention, cal)
        
    if months:
        target_date = adjust(addMonths(target_date, months, end_of_month), convention, cal)
        
    if weeks:
        target_date = adjust(target_date + timedelta(days=7*weeks), convention)

    if days:
        target_date = addBusinessDays(target_date, days, cal)
        
    
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

if __name__ == "__main__":
    print(weekOfYear(date(2017, 1, 1), True)) # 52
    print(weekOfYear(date(2017, 1, 1), False)) # 1
    print(weekOfYear(date(2017, 6, 1), True)) # 22
    print(weekOfYear(date(2017, 6, 1), False)) # 22
    print(weekOfYear(date(2017, 12, 1), True)) # 48
    print(weekOfYear(date(2017, 12, 1), False)) # 48
    print(weekOfYear(date(2017, 12, 31), True)) # 52
    print(weekOfYear(date(2017, 12, 31), False)) # 53
    