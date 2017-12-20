from enum import IntEnum
from datetime import datetime, timedelta
import math
    
class Season(IntEnum):
    SPRING = 0
    SUMMER = 90
    AUTUMN = 180
    WINTER = 270

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
