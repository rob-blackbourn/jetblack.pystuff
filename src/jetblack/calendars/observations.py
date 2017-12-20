from mpmath import mpf
import math
from jetblack.calendars.timemath import Clock
from jetblack.calendars.location import URBANA
from jetblack.calendars.solar import solar_longitude_after, solar_longitude
from jetblack.calendars.astrological import declination
from jetblack.calendars.months import MonthOfYear
from jetblack.calendars.weekdays import DayOfWeek
from jetblack.calendars.seasons import Season
from jetblack.calendars.systems.gregorian import GregorianDate
from jetblack.calendars.trigonometry import angle, arctan_degrees, tan_degrees
from jetblack.calendars.location import Location
from jetblack.calendars.lunar import MoonPhase, lunar_phase_at_or_after


def urbana_sunset(gdate):
    """Return sunset time in Urbana, Ill, on Gregorian date 'gdate'."""
    return Clock.time_from_moment(URBANA.sunset(gdate.to_fixed()))

def urbana_winter(g_year):
    """Return standard time of the winter solstice in Urbana, Illinois, USA."""
    return URBANA.standard_from_universal(solar_longitude_after(Season.WINTER, GregorianDate(g_year, MonthOfYear.JANUARY, 1).to_fixed()))

def jewish_dusk(date, location):
    """Return standard time of Jewish dusk on fixed date, date,
    at location, location, (as per Vilna Gaon)."""
    return location.dusk(date, angle(4, 40, 0))

def jewish_sabbath_ends(date, location):
    """Return standard time of end of Jewish sabbath on fixed date, date,
    at location, location, (as per Berthold Cohn)."""
    return location.dusk(date, angle(7, 5, 0)) 

def jewish_morning_end(date, location):
    """Return standard time on fixed date, date, at location, location,
    of end of morning according to Jewish ritual."""
    return location.standard_from_sundial(date + Clock.days_from_hours(10))

def asr(date, location):
    """Return standard time of asr on fixed date, date,
    at location, location."""
    noon = location.universal_from_standard(location.midday(date))
    phi = location.latitude
    delta = declination(noon, 0, solar_longitude(noon))
    altitude = delta - phi - 90
    h = arctan_degrees(tan_degrees(altitude), 2 * tan_degrees(altitude) + 1)
    # For Shafii use instead:
    # tan_degrees(altitude) + 1)
    return location.dusk(date, -h)

JERUSALEM = Location(mpf(31.8), mpf(35.2), 800, Clock.days_from_hours(2))

def astronomical_easter(g_year):
    """Return date of (proposed) astronomical Easter in Gregorian
    year, g_year."""
    jan1 = GregorianDate.new_year(g_year)
    equinox = solar_longitude_after(Season.SPRING, jan1)
    paschal_moon = int(math.floor(JERUSALEM.apparent_from_local(JERUSALEM.local_from_universal(lunar_phase_at_or_after(MoonPhase.FULL, equinox)))))
    # Return the Sunday following the Paschal moon.
    return DayOfWeek(DayOfWeek.SUNDAY).after(paschal_moon)