import csv
import json
import random
import time
import backtrader as bt
import datetime

from message import DingTalkService
from setting import date_root_path


def date2csv(data, file_name, head, write_type=None):
    """
    数据保存为csv
    :param data: 数据
    :param file_name: 文件名称
    :param head: 表头
    :return: 文件保存路径
    """
    if write_type is None:
        write_type = 'w'
    file_path = date_root_path + file_name + ".csv"
    with open(file_path, write_type) as csvfile:
        writer = csv.writer(csvfile, lineterminator='\n')
        writer.writerow(head)
        writer.writerows(data)
    return file_path


def generate_random_str(randomlength=16):
    """
    生成一个指定长度的随机字符串
    """
    random_str = ''
    base_str = 'ABCDEFGHIGKLMNOPQRSTUVWXYZabcdefghigklmnopqrstuvwxyz0123456789'
    length = len(base_str) - 1
    for i in range(randomlength):
        random_str += base_str[random.randint(0, length)]
    return random_str


def send_text_to_dingtalk(message: str):
    DingTalkService().send_text(message)


def load_csv_data(data_path, size=None, start=None, end=None):
    return bt.feeds.GenericCSVData(
        dataname=data_path,
        nullvalue=0.0,
        fromdate=start,
        todate=end,
        dtformat="%Y-%m-%d %H:%M:%S",
        timeframe=bt.TimeFrame.Minutes,
        datetime=0,
        high=1,
        low=2,
        open=3,
        close=4,
        volume=5,
        openinterest=-1
    )


def str2timestamp(date: str, format="%Y-%m-%d %H:%M:%S"):
    """
    时间戳转字符串
    :param date:
    :param format:
    :return:
    """
    time_array = time.strptime(date, format)
    timestamp = int(time.mktime(time_array))
    return timestamp


def timestamp2str(date: int, format="%Y-%m-%d %H:%M:%S"):
    time_array = time.localtime(date)
    style_time = time.strftime(format, time_array)
    return style_time


def add_year(date, years):
    result = date + datetime.timedelta(366 * years)
    if years > 0:
        while result.year - date.year > years or date.month < result.month or date.day < result.day:
            result += datetime.timedelta(-1)

    elif years < 0:
        while result.year - date.year < years or date.month > result.month or date.day > result.day:
            result += datetime.timedelta(1)

    return result


def get_end_year(date: datetime.datetime):
    year = date.year
    return datetime.datetime(year, 12, 31)


def add_mouth(data: datetime.datetime, mouth: int):
    """"""
    if mouth > 0:
        return data + datetime.timedelta(days=mouth * 30)
    return data - datetime.timedelta(days=mouth * 30)


def to_json(data):
    return json.dumps(data, indent=4, separators=(',', ':'), ensure_ascii=False)


def save_to_text(data, path):
    with open(path, 'w') as f:
        f.write(data)
