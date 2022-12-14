# -*- coding: UTF-8 -*-
import datetime

import logging
import time
import backtrader
import numpy
import pandas
import os
from util import file_util, date_util
import constant
from binance.spot import Spot
import tqdm
from constant.config import COIN_ROOT_DIR


def get_local_generic_csv_data(symbol: str, interval: str, coin="USDT"):
    # 文件名称
    symbol = symbol + coin
    file_name = symbol + ".csv"
    # 文件位置
    path = COIN_ROOT_DIR + f"\\{interval}\\" + file_name
    # 是否更新数据
    if os.path.exists(path):
        return load_generic_csv_data(path)
    raise FileNotFoundError(f"{path}")


def get_local_file_path(symbol: str, interval: str, coin="USDT"):
    """
    获取数据的本地路径
    :param symbol:
    :param interval:
    :param coin:
    :return:
    """
    # 文件名称
    file_name = symbol + coin
    # 文件位置
    path = COIN_ROOT_DIR + f"\\{interval}\\" + file_name + ".csv"
    return path


def get_k_lines_asc(symbol: str, interval: str, coin='USDT', start_time: int = None,
                    end_time: int = datetime.datetime.now().timestamp() * 1000):
    """
    获取k线数据 从结束时间 正序
    :param coin:
    :param symbol: 虚拟货币类型
    :param interval: 时间基本
    :param start_time:
    :param end_time:
    :return:
    """

    proxies = {'https': 'https://127.0.0.1:7890'}
    client = Spot(proxies=proxies)
    stop_time = end_time
    if start_time is None:
        start_time = get_earliest_start_time(symbol, coin)
        end_time = datetime.datetime.now().timestamp() * 1000
        stop_time = datetime.datetime.now().timestamp() * 1000
    end_time = start_time + constant.interval_second[interval] * 1000 * 300

    if stop_time > end_time:
        stop_time = datetime.datetime.now().timestamp() * 1000
        end_time = start_time + constant.interval_second[interval] * 1000 * 399
    init_time = start_time
    query_symbol = symbol + coin
    data = []
    size = (stop_time - start_time) / 1000 / constant.interval_second[interval] / 300 + 1

    pbar = tqdm.trange(0, int(size), 1)
    for idx, element in enumerate(pbar):
        response = client.klines(query_symbol, interval, startTime=int(start_time), endTime=int(end_time))

        # 解析数据
        k_lines = parse_k_lines(response)

        if len(k_lines) > 0:
            data.extend(k_lines)
        if start_time > stop_time or stop_time < end_time:
            # 没数据返回 || 到要求的数据
            pbar.set_description(f"No.{idx}: [down-{symbol}-{interval}]")
            logging.info(
                f"【下载数据】 【{symbol}-{interval}】 "
                f"【{date_util.timestamp2str(init_time / 1000)}  {date_util.timestamp2str(stop_time / 1000)}】")

            break
        pbar.set_description(
            f"No.{idx}: [{symbol}-{interval}]")
        if len(k_lines) == 0:
            logging.info(f"数据缺失 [{date_util.timestamp2str(start_time / 1000)}]")
            start_time = end_time + constant.interval_second[interval] * 1000
        else:
            start_time = response[-1][0] + constant.interval_second[interval] * 1000
        end_time = start_time + constant.interval_second[interval] * 1000 * 300

        if end_time > stop_time:
            end_time = stop_time
    return data


def get_k_lines_desc(symbol: str, interval: str, coin='USDT', start_time: int = None,
                     end_time: int = datetime.datetime.now().timestamp() * 1000):
    """
    获取k线数据 从结束时间 倒序获取
    :param symbol: 虚拟货币类型
    :param interval: 时间基本
    :param start_time:
    :param end_time:
    :return:
    """

    proxies = {'https': 'https://127.0.0.1:7890'}
    client = Spot(proxies=proxies)
    # 结束查询时间
    query_symbol = symbol + coin
    stop_time = start_time
    if stop_time is None:
        stop_time = 0
    if start_time is None or end_time is None:
        # 获取数据
        response = client.klines(query_symbol, interval)
        start_time = response[0][0]
        end_time = response[-1][0]

    data = []
    pbar = tqdm.trange(0, 10000, 1)
    for idx, element in enumerate(pbar):
        response = client.klines(query_symbol, interval, startTime=int(start_time), endTime=int(end_time))
        # 解析数据

        k_lines = parse_k_lines(response)
        k_lines.reverse()
        data.extend(k_lines)
        if len(k_lines) == 0 or len(k_lines) == 1 or stop_time > start_time:
            # 没数据返回 || 到要求的数据

            pbar.set_description(f"No.{idx}: [down_data] [total][{len(data)}]")
            break
        pbar.set_description(
            f"No.{idx}: [down_data]-[{symbol}-{interval}]")
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


def get_time_timeframe(interval):
    if interval is None:
        timeframe = backtrader.TimeFrame.Minutes
    elif interval == '1d':
        timeframe = backtrader.TimeFrame.Days
    else:
        timeframe = backtrader.TimeFrame.Minutes
    return timeframe


def load_generic_csv_data(data_path, interval=None, start=None, end=None):
    return backtrader.feeds.GenericCSVData(
        dataname=data_path,
        nullvalue=0.0,
        fromdate=start,
        todate=end,
        dtformat="%Y-%m-%d %H:%M:%S",
        timeframe=get_time_timeframe(interval),
        datetime=0,
        high=1,
        low=2,
        open=3,
        close=4,
        volume=5,
        openinterest=-1
    )


def get_earliest_start_time(symbol, coin='USDT'):
    """
    获取数据测开始时间
    通过获取日线级别的时间
    :param symbol:
    :param coin:
    :return:
    """
    path = get_local_file_path(symbol, '1d', coin=coin)

    if not os.path.exists(path):
        # 获取数据
        data = get_k_lines_desc(symbol, '1d', coin=coin)
        file_util.date2csv(data, path, constant.k_lines_csv_head, write_type='a')
        start_time = date_util.str2datetime(data[0][0]).timestamp() * 1000

    else:
        data = numpy.array(pandas.read_csv(path))
        latest_record_time = date_util.str2datetime(data[0][0])
        start_time = latest_record_time.timestamp() * 1000
    return int(start_time)


def down_load_data(symbol, interval: str, coin='USDT'):
    """
    下载数据
    :param symbol:
    :param interval:
    :param coin:
    :return:
    """
    path = get_local_file_path(symbol, interval, coin)

    if os.access(path, os.X_OK):
        # 文件存在
        data = numpy.array(pandas.read_csv(path))
        latest_record_time = date_util.str2datetime(data[-1][0])
        start_time = date_util.add_time(latest_record_time, minutes=int(constant.interval_second[interval] / 60))
        # 获取数据
        data = get_k_lines_asc(symbol, interval, coin, start_time=start_time.timestamp() * 1000)
    else:
        # 本地没有数据
        data = get_k_lines_asc(symbol, interval, coin, )
    # 保存数据
    if data:
        file_util.date2csv(data, path, constant.k_lines_csv_head, 'a')


def bath_down_load_data(symbols, intervals, coin='USDT'):
    """
    批量下载数据
    :param symbols:
    :param intervals:
    :param coin:
    :return:
    """
    for symbol in symbols:
        for interval in intervals:
            logging.info(f"【下载数据】 【{symbol}-{interval}】")
            down_load_data(symbol, interval, coin)
