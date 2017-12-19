import unittest
from jetblack.calendars import DayOfWeek
from jetblack.calendars.datemath import weekday_fromordinal


class TestDayArithmatic(unittest.TestCase):

    def setUp(self):
        self.data = {
            -214193: DayOfWeek.SUNDAY,
            -61387 : DayOfWeek.WEDNESDAY,
            25469  : DayOfWeek.WEDNESDAY,
            49217  : DayOfWeek.SUNDAY,
            171307 : DayOfWeek.WEDNESDAY,
            210155 : DayOfWeek.MONDAY,
            253427 : DayOfWeek.SATURDAY,
            369740 : DayOfWeek.SUNDAY,
            400085 : DayOfWeek.SUNDAY,
            434355 : DayOfWeek.FRIDAY,
            452605 : DayOfWeek.SATURDAY,
            470160 : DayOfWeek.FRIDAY,
            473837 : DayOfWeek.SUNDAY,
            507850 : DayOfWeek.SUNDAY,
            524156 : DayOfWeek.WEDNESDAY,
            544676 : DayOfWeek.SATURDAY,
            567118 : DayOfWeek.SATURDAY,
            569477 : DayOfWeek.SATURDAY,
            601716 : DayOfWeek.WEDNESDAY,
            613424 : DayOfWeek.SUNDAY,
            626596 : DayOfWeek.FRIDAY,
            645554 : DayOfWeek.SUNDAY,
            664224 : DayOfWeek.MONDAY,
            671401 : DayOfWeek.WEDNESDAY,
            694799 : DayOfWeek.SUNDAY,
            704424 : DayOfWeek.SUNDAY,
            708842 : DayOfWeek.MONDAY,
            709409 : DayOfWeek.MONDAY,
            709580 : DayOfWeek.THURSDAY,
            727274 : DayOfWeek.TUESDAY,
            728714 : DayOfWeek.SUNDAY,
            744313 : DayOfWeek.WEDNESDAY,
            764652 : DayOfWeek.SUNDAY }

    def testKnownData(self):
        for (ordinal, day_of_week) in self.data.items():
            self.assertEqual(day_of_week, weekday_fromordinal(ordinal))


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()