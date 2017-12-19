import math
from mpmath import mpf, degrees, radians, sin, cos, tan, asin, acos, atan

def secs(x):
    """Return the seconds in angle x."""
    return x / 3600.0

def angle(d, m, s):
    """Return an angle data structure
    from d degrees, m arcminutes and s arcseconds.
    This assumes that negative angles specifies negative d, m and s."""
    return d + ((m + (s / 60)) / 60)

def normalized_degrees(theta):
    """Return a normalise angle theta to range [0,360) degrees."""
    return theta % 360

def normalized_degrees_from_radians(theta):
    """Return normalized degrees from radians, theta.
    Function 'degrees' comes from mpmath."""
    return normalized_degrees(degrees(theta))

def sin_degrees(theta):
    """Return sine of theta (given in degrees)."""
    return sin(radians(theta))

def cos_degrees(theta):
    """Return cosine of theta (given in degrees)."""
    return cos(radians(theta))

def tan_degrees(theta):
    """Return tangent of theta (given in degrees)."""
    return tan(radians(theta))

def arctan_degrees(y, x):
    """ Arctangent of y/x in degrees."""
    if x == 0 and y != 0:
        return (math.copysign(1, y) * mpf(90)) % 360
    else:
        alpha = normalized_degrees_from_radians(atan(y / x))
        if x >= 0:
            return alpha
        else:
            return (alpha + mpf(180)) % 360

def arcsin_degrees(x):
    """Return arcsine of x in degrees."""
    return normalized_degrees_from_radians(asin(x))

def arccos_degrees(x):
    """Return arccosine of x in degrees."""
    return normalized_degrees_from_radians(acos(x))

class DegreeMinutesSeconds(object):
    
    def __init__(self, degrees, minutes, seconds):
        self.degress = degrees
        self.minutes = minutes
        self.seconds = seconds

    @classmethod        
    def from_angle(cls, alpha):
        """Return an angle in degrees:minutes:seconds from angle,
        'alpha' in degrees."""
        d = int(math.floor(alpha))
        m = int(math.floor(60 * (alpha % 1)))
        s = (alpha * 60 * 60) % 60
        return DegreeMinutesSeconds(d, m, s)
    
    def to_angle(self):
        return self.degress + ((self.minutes + (self.seconds / 60)) / 60)
    