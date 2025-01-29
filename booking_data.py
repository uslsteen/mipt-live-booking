from datetime import date
import datetime

def get_next_date(base: date, offset: int) -> date:
    if isinstance(base, date):
        return base + datetime.timedelta(days=offset)
    else:
        return None

def get_next_week(base: date = date.today()) -> list:
    week_lenght = 8
    if isinstance(base, date):
        return [BookingSlot(data=get_next_date(base, i))
                for i in range(week_lenght)]
    else:
        return None

class BookingTime():
    def __init__(self, start=None, end=None):
        self.start = start
        self.end = end
    #
    def __str__(self):
        return self.start
    #
    def to_dict(self, recursive=True):
        return {
            "start": self.start,
            "end": self.end,
        }

    """
        Serialize BookingTime into string bot-readable representation
        Callback function to provide BookingTime data into date button
    """
    @staticmethod
    def serialize(other):
        if isinstance(other, BookingTime):
            return f"time_{other.start}"
        else:
            return None

    """
        Deserialize string representation into BookingTime
    """
    @staticmethod
    def deserialize(data: str):
        splitted = data.split('_')
        return BookingTime(start=splitted[1])
    #
#
class BookingSlot():
    WEEKDAYS = 4

    def __init__(self, data: datetime.date = None, date: str = None, weekday: int = None, time: BookingTime = None):
        if data != None:
            self.date: str = str(data)
            self.weekday: int = int(data.weekday())
            self.time: BookingTime = None
        else:
            self.date = date
            self.weekday = weekday
            self.time = time
    #

    @property
    def is_weekend(self):
        return self.weekday > BookingSlot.WEEKDAYS
    #
    @property
    def is_valid(self):
        return (self.date, self.weekday, self.time) != (None, None, None)
    #
    def __str__(self):
        return self.date
    #
    def to_dict(self, recursive=True):
        return {
            "date": self.date,
            "weekday": self.weekday,
            "time": str(self.time),
        }

    """
        Serialize BookingSlot into string bot-readable representation
        Callback function to provide BookingSlot data into date button
    """
    @staticmethod
    def serialize(other):
        if isinstance(other, BookingSlot):
            return f"date_{other.date}_{other.weekday}"
        else:
            return None

    """
        Deserialize string representation into BookingSlot
    """
    @staticmethod
    def deserialize(data: str):
        splitted = data.split('_')
        return BookingSlot(date=splitted[1], weekday=int(splitted[2]))
    #
#
