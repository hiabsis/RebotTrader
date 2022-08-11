# -*- coding: UTF-8 -*-
import datetime
import json
import pprint
import time


def add_time(date, minutes=0, hour=0, days=0):
    date = date + datetime.timedelta(minutes=minutes, hours=hour, days=days)
    return date


def timestamp2str(timestamp, fmt="%Y-%m-%d %H:%M:%S"):
    time_array = time.localtime(timestamp)
    return time.strftime(fmt, time_array)


def str2timestamp(date: str, fmt="%Y-%m-%d %H:%M:%S"):
    """
    时间戳转字符串
    :param fmt:
    :param date:
    :return:
    """
    time_array = time.strptime(date, fmt)
    timestamp = int(time.mktime(time_array))
    return timestamp


def str2datetime(date_str: str, fmt="%Y-%m-%d %H:%M:%S"):
    return datetime.datetime.strptime(date_str, fmt)


if __name__ == '__main__':
    print(datetime.datetime.now() + datetime.timedelta(minutes=-1, hours=0))
