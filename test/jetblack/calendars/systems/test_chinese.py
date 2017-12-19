import unittest
from jetblack.calendars.systems.chinese import ChineseDate
from jetblack.calendars.systems.gregorian import GregorianDate

class Test(unittest.TestCase):

    def testNewYear(self):
        self.assertEqual(ChineseDate.new_year(2015), GregorianDate(2015, 2, 19).toordinal(), "Thursday, 19 February 2015")
        self.assertEqual(ChineseDate.new_year(2016), GregorianDate(2016, 2, 8).toordinal(), "Monday, 8 February 2016")
        self.assertEqual(ChineseDate.new_year(2017), GregorianDate(2017, 1, 28).toordinal(), "Saturday, 28 January 2017")
        self.assertEqual(ChineseDate.new_year(2018), GregorianDate(2018, 2, 16).toordinal(), "Friday, 16 February 2018")

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testNewYear']
    unittest.main()