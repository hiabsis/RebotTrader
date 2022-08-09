import datetime
import time
import backtrader
import setting
import numpy
import pandas
import os
from util import file_util, date_util
import constant
from binance.spot import Spot


def get_local_generic_csv_data(symbol: str, interval: str, coin="USDT"):
    # 文件名称
    symbol = symbol + coin
    file_name = symbol + "_" + interval + ".csv"
    # 文件位置
    path = setting.date_root_path + "\\" + file_name
    # 是否更新数据
    if os.path.exists(path):
        return load_generic_csv_data(path)
    raise FileNotFoundError(f" {path}")


def get_generic_csv_data(symbol: str, interval: str, start_time: datetime.datetime = None,
                         end_time: datetime.datetime = datetime.datetime.now()):
    """
    加载数据
    默认加载全部数据
    :param symbol: 货币品种
    :param interval:时间级别
    :param start_time: 开始时间
    :param end_time:结束时间 默认当前时间
    :return:
    """
    # 文件名称
    file_name = symbol + "_" + interval
    # 文件位置
    path = setting.date_root_path + "\\" + file_name + ".csv"
    # 是否更新数据

    if os.access(path, os.X_OK):
        # 文件存在
        data = numpy.array(pandas.read_csv(path))
        # 最早数据记录

        earliest_record_time = date_util.str2datetime(data[0][0])
        latest_record_time = date_util.str2datetime(data[-1][0])

        if start_time is None:
            # 未设置开始时间
            start_time = earliest_record_time
        if start_time.timestamp() >= earliest_record_time.timestamp() or end_time.timestamp() <= latest_record_time.timestamp():
            # 本地数据可以满足需求

            return load_generic_csv_data(path, start_time, end_time)
        start_time = latest_record_time

    # 获取数据
    data = get_k_lines(symbol, interval, start_time=start_time, end_time=end_time)
    # 保存数据
    file_util.date2csv(data, file_name, constant.k_lines_csv_head, 'a')
    return load_generic_csv_data(path, start_time, end_time)


def get_k_lines(symbol: str, interval: str, start_time: int = None,
                end_time: int = datetime.datetime.now().timestamp()):
    """
    获取k线数据
    :param symbol: 虚拟货币类型
    :param interval: 时间基本
    :param start_time:
    :param end_time:
    :return:
    """
    proxies = {'https': 'https://127.0.0.1:7890'}
    client = Spot(proxies=proxies)
    # 结束查询时间
    stop_time = start_time
    if start_time is None or end_time is None:
        # 获取数据
        response = client.klines(symbol, interval)
        start_time = response[0][0]
        print(response[-1][0])
        end_time = response[-1][0]
        stop_time = datetime.datetime(1999, 4, 5).timestamp()
    # 返回的数据
    data = []
    while True:
        # 获取数据
        if stop_time >= start_time:
            start_time = start_time
            stop_time = None
        response = client.klines(symbol, interval, startTime=start_time, endTime=end_time)
        # 解析数据
        k_lines = parse_k_lines(response)
        data.extend(k_lines)
        if len(k_lines) == 0 or stop_time is None:
            # 没数据返回 || 到要求的数据
            break
        # 计算下一周期的开始结束数据
        end_time = response[0][0] - constant.interval_second[interval] * 1000
        start_time = response[0][0] - constant.interval_second[interval] * 1000 * 400
    data.reverse()
    return data


def parse_k_lines(response):
    """
    解析返回的k线数据
    :param response:
    :return:
    """
    k_lines = []
    for item in response:
        k_line = []
        # 开盘时间
        time_array = time.localtime(item[0] / 1000)
        k_line.append(time.strftime('%Y-%m-%d %H:%M:%S', time_array))
        # 开盘价格
        k_line.append(item[1])
        # 收盘价格
        k_line.append(item[4])
        # 最高价格
        k_line.append(item[2])
        # 最低价格
        k_line.append(item[3])
        # 交易量
        k_line.append(item[5])
        k_lines.append(k_line)
    return k_lines


def load_generic_csv_data(data_path, start=None, end=None):
    return backtrader.feeds.GenericCSVData(
        dataname=data_path,
        nullvalue=0.0,
        fromdate=start,
        todate=end,
        dtformat="%Y-%m-%d %H:%M:%S",
        timeframe=backtrader.TimeFrame.Minutes,
        datetime=0,
        high=1,
        low=2,
        open=3,
        close=4,
        volume=5,
        openinterest=-1
    )
