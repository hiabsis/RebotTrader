import datetime
import time

INTERVAL_CORN_DICT = {
    '10s': "0/10 * * * * ? ",
    "1m": "0 0/1 * * * ? ",
    "3m": "0 0/3 * * * ? ",
    "5m": "0 0/5 * * * ? ",
    "15m": "0 0/15 * * * ? ",
    "30m": "0 0/30 * * * ? ",
    "1h": "0 0 0/1 * * ? ",
    "2h": "0 0 0/2 * * ? ",
    "4h": "0 0 0/4 * * ? ",
    "6h": "0 0 0/6 * * ? ",
    "1d": "0 0 0 1/1 * ? ",
}
DEFAULT_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
INTERVAL_SECOND_DICT = {
    "1m": 60,
    "3m": 180,
    "5m": 300,
    "15m": 900,
    "30m": 1800,
    "1h": 3600,
    "2h": 72000,
    "4h": 14400,
    "6h": 21600,
    "12h": 43200,
    "1d": 86400,
}


class DateUtil:

    @staticmethod
    def add_minutes(minute: int, date: datetime.datetime = datetime.datetime.now()):
        return date + datetime.timedelta(minutes=minute)

    @staticmethod
    def add_hour(hour: int, date: datetime.datetime = datetime.datetime.now()):
        return date + datetime.timedelta(hours=hour)

    @staticmethod
    def add_day(day: int, date: datetime.datetime = datetime.datetime.now()):
        return date + datetime.timedelta(days=day)

    @staticmethod
    def add_second(second: int, date: datetime.datetime = datetime.datetime.now()):
        return date + datetime.timedelta(seconds=second)

    @staticmethod
    def timestamp2str(timestamp, fmt="%Y-%m-%d %H:%M:%S"):
        time_array = time.localtime(timestamp)
        return time.strftime(fmt, time_array)

    @staticmethod
    def date2str(date: datetime.datetime, fmt="%Y-%m-%d %H:%M:%S"):
        return DateUtil.timestamp2str(date.timestamp(), fmt)

    @staticmethod
    def interval2minute(interval):
        return DateUtil.interval2second(interval) / DateUtil.interval2second('1m')

    @staticmethod
    def interval2second(interval):
        """
        时间转为秒
        :param interval:
        :return:
        """
        return INTERVAL_SECOND_DICT[interval]

    @staticmethod
    def interval2corn(interval):
        return INTERVAL_CORN_DICT[interval]
