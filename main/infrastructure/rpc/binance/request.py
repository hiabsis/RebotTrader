import time
from datetime import datetime

from main.infrastructure.utils.date import DateUtil


class QueryKLinesByTime(object):
    """
    查询k线
    """

    def __init__(self, symbol, interval, start: datetime = None, end: datetime = None):
        self.symbol = symbol
        self.interval = interval
        self.start = int(time.mktime(start.timetuple())) * 1000
        self.end = int(time.mktime(end.timetuple())) * 1000


class QueryLatestKLinesRequest(object):
    """
    查询最新的k线
    """

    def __init__(self, symbol, interval, limit: int):
        self.symbol = symbol
        self.interval = interval
        end = datetime.now()
        start = DateUtil.add_second(-1 * limit * DateUtil.interval2second(interval), datetime.now())
        self.start = int(time.mktime(start.timetuple())) * 1000
        self.end = int(time.mktime(end.timetuple())) * 1000


class QueryLatestFuturesKlinesRequest:
    def __init__(self, symbol, interval, limit: int):
        self.symbol = symbol
        self.interval = interval
        end = datetime.now()
        start = DateUtil.add_second(-1 * limit * DateUtil.interval2second(interval), datetime.now())
        self.start = int(time.mktime(start.timetuple())) * 1000
        self.end = int(time.mktime(end.timetuple())) * 1000

