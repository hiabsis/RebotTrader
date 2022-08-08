import datetime
from datetime import time


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
    return datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
