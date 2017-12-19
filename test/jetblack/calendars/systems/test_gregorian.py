import unittest
from jetblack.calendars.systems.gregorian import GregorianDate


class TestGregorian(unittest.TestCase):


    def testRoundTrip(self):
        d1 = GregorianDate(2017, 12, 19)
        o = d1.toordinal()
        d2 = GregorianDate.fromordinal(o)
        self.assertEqual(d1, d2, "Should round trip")
         


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'TestGregorian.testRoundTrip']
    unittest.main()