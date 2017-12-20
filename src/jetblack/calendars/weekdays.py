from enum import IntEnum

class DayOfWeek(IntEnum):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6
    
    
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
