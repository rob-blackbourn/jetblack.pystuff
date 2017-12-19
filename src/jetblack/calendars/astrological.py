from mpmath import mpf, pi
import math
from jetblack.calendars.datemath import MonthOfYear
from jetblack.calendars.timemath import Clock
from jetblack.calendars.systems.gregorian import GregorianDate
from jetblack.calendars.utils import poly, signum
from jetblack.calendars.trigonometry import angle, sin_degrees, cos_degrees, tan_degrees, arcsin_degrees, arctan_degrees, secs

J2000 = Clock.days_from_hours(mpf(12)) + GregorianDate.new_year(2000)

def zone_from_longitude(phi):
    """Return the difference between UT and local mean time at longitude
    'phi' as a fraction of a day."""
    return phi / 360

def ephemeris_correction(tee):
    """Return Dynamical Time minus Universal Time (in days) for
    moment, tee.  Adapted from "Astronomical Algorithms"
    by Jean Meeus, Willmann_Bell, Inc., 1991."""
    year = GregorianDate.to_year(int(math.floor(tee)))
    c = GregorianDate.date_difference(GregorianDate(1900, MonthOfYear.JANUARY, 1), GregorianDate(year, MonthOfYear.JULY, 1)) / mpf(36525)
    if 1988 <= year <= 2019:
        return 1/86400 * (year - 1933)
    elif 1900 <= year <= 1987:
        return poly(c, [mpf(-0.00002), mpf(0.000297), mpf(0.025184), mpf(-0.181133), mpf(0.553040), mpf(-0.861938), mpf(0.677066), mpf(-0.212591)])
    elif 1800 <= year <= 1899:
        return poly(c, [mpf(-0.000009), mpf(0.003844), mpf(0.083563), mpf(0.865736), mpf(4.867575), mpf(15.845535), mpf(31.332267), mpf(38.291999), mpf(28.316289), mpf(11.636204), mpf(2.043794)])
    elif 1700 <= year <= 1799:
        return 1/86400 * poly(year - 1700, [8.118780842, -0.005092142, 0.003336121, -0.0000266484])
    elif 1620 <= year <= 1699:
        return 1/86400 * poly(year - 1600, [mpf(196.58333), mpf(-4.0675), mpf(0.0219167)])
    else:
        x = Clock.days_from_hours(mpf(12)) + GregorianDate.date_difference(GregorianDate(1810, MonthOfYear.JANUARY, 1), GregorianDate(year, MonthOfYear.JANUARY, 1))
        return 1/86400 * (((x * x) / mpf(41048480)) - 15)

def universal_from_dynamical(tee):
    """Return Universal moment from Dynamical time, tee."""
    return tee - ephemeris_correction(tee)

def dynamical_from_universal(tee):
    """Return Dynamical time at Universal moment, tee."""
    return tee + ephemeris_correction(tee)

def julian_centuries(tee):
    """Return Julian centuries since 2000 at moment tee."""
    return (dynamical_from_universal(tee) - J2000) / mpf(36525)

def obliquity(tee):
    """Return (mean) obliquity of ecliptic at moment tee."""
    c = julian_centuries(tee)
    return (angle(23, 26, mpf(21.448)) +
            poly(c, [mpf(0),
                     angle(0, 0, mpf(-46.8150)),
                     angle(0, 0, mpf(-0.00059)),
                     angle(0, 0, mpf(0.001813))]))

def equation_of_time(tee):
    """Return the equation of time (as fraction of day) for moment, tee.
    Adapted from "Astronomical Algorithms" by Jean Meeus,
    Willmann_Bell, Inc., 1991."""
    c = julian_centuries(tee)
    lamb = poly(c, [mpf(280.46645), mpf(36000.76983), mpf(0.0003032)])
    anomaly = poly(c, [mpf(357.52910), mpf(35999.05030), mpf(-0.0001559), mpf(-0.00000048)])
    eccentricity = poly(c, [mpf(0.016708617), mpf(-0.000042037), mpf(-0.0000001236)])
    varepsilon = obliquity(tee)
    y = pow(tan_degrees(varepsilon / 2), 2)
    equation = ((1/2 / pi) *
                (y * sin_degrees(2 * lamb) +
                 -2 * eccentricity * sin_degrees(anomaly) +
                 (4 * eccentricity * y * sin_degrees(anomaly) *
                  cos_degrees(2 * lamb)) +
                 -0.5 * y * y * sin_degrees(4 * lamb) +
                 -1.25 * eccentricity * eccentricity * sin_degrees(2 * anomaly)))
    return signum(equation) * min(abs(equation), Clock.days_from_hours(mpf(12)))

def precise_obliquity(tee):
    """Return precise (mean) obliquity of ecliptic at moment tee."""
    u = julian_centuries(tee) / 100
    #assert(abs(u) < 1,
    #       'Error! This formula is valid for +/-10000 years around J2000.0')
    return (poly(u, [angle(23, 26, mpf(21.448)),
                     angle(0, 0, mpf(-4680.93)),
                     angle(0, 0, mpf(-   1.55)),
                     angle(0, 0, mpf(+1999.25)),
                     angle(0, 0, mpf(-  51.38)),
                     angle(0, 0, mpf(- 249.67)),
                     angle(0, 0, mpf(-  39.05)),
                     angle(0, 0, mpf(+   7.12)),
                     angle(0, 0, mpf(+  27.87)),
                     angle(0, 0, mpf(+   5.79)),
                     angle(0, 0, mpf(+   2.45))]))

def declination(tee, beta, lam):
    """Return declination at moment UT tee of object at
    longitude 'lam' and latitude 'beta'."""
    varepsilon = obliquity(tee)
    return arcsin_degrees(
        (sin_degrees(beta) * cos_degrees(varepsilon)) +
        (cos_degrees(beta) * sin_degrees(varepsilon) * sin_degrees(lam)))

def right_ascension(tee, beta, lam):
    """Return right ascension at moment UT 'tee' of object at
    latitude 'lam' and longitude 'beta'."""
    varepsilon = obliquity(tee)
    return arctan_degrees((sin_degrees(lam) * cos_degrees(varepsilon)) - (tan_degrees(beta) * sin_degrees(varepsilon)), cos_degrees(lam))

def sidereal_from_moment(tee):
    """Return the mean sidereal time of day from moment tee expressed
    as hour angle.  Adapted from "Astronomical Algorithms"
    by Jean Meeus, Willmann_Bell, Inc., 1991."""
    c = (tee - J2000) / mpf(36525)
    return poly(c, [mpf(280.46061837), mpf(36525) * mpf(360.98564736629), mpf(0.000387933), mpf(-1)/mpf(38710000)]) % 360

def nutation(tee):
    """Return the longitudinal nutation at moment, tee."""
    c = julian_centuries(tee)
    cap_A = poly(c, [mpf(124.90), mpf(-1934.134), mpf(0.002063)])
    cap_B = poly(c, [mpf(201.11), mpf(72001.5377), mpf(0.00057)])
    return (mpf(-0.004778)  * sin_degrees(cap_A) + 
            mpf(-0.0003667) * sin_degrees(cap_B))

def aberration(tee):
    """Return the aberration at moment, tee."""
    c = julian_centuries(tee)
    return ((mpf(0.0000974) *
             cos_degrees(mpf(177.63) + mpf(35999.01848) * c)) -
            mpf(0.005575))

def precession(tee):
    """Return the precession at moment tee using 0,0 as J2000 coordinates.
    Adapted from "Astronomical Algorithms" by Jean Meeus,
    Willmann-Bell, Inc., 1991."""
    c = julian_centuries(tee)
    eta = poly(c, [0, secs(mpf(47.0029)), secs(mpf(-0.03302)), secs(mpf(0.000060))]) % 360
    cap_P = poly(c, [mpf(174.876384), secs(mpf(-869.8089)), secs(mpf(0.03536))]) % 360
    p = poly(c, [0, secs(mpf(5029.0966)), secs(mpf(1.11113)), secs(mpf(0.000006))]) % 360
    cap_A = cos_degrees(eta) * sin_degrees(cap_P)
    cap_B = cos_degrees(cap_P)
    arg = arctan_degrees(cap_A, cap_B)

    return (p + cap_P - arg) % 360