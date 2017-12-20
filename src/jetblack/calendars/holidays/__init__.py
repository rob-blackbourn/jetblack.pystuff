from jetblack.calendars.weekdays import DayOfWeek

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