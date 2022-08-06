import time

from binance.spot import Spot
from constant import k_lines_csv_head, interval_second
from util.file_util import date2csv
from utils import timestamp2str
import requests
import json
import pandas as pd
import datetime as dt

client = Spot()


class GetKLinesRequest:
    def __init__(self, symbol, interval, limit=None, startTime=None, endTime=None):
        # 类型
        self.symbol = symbol
        # 时间级别
        self.interval = interval
        # 限制数量
        self.limit = limit
        #  开始时间
        self.startTime = startTime
        # 结束时间
        self.endTime = endTime


def get_k_lines_by_request(request: GetKLinesRequest):
    response = client.klines(request.symbol, request.interval, limit=request.limit)
    return parse_k_lines(response)


def get_k_lines(symbol, interval, limit=400):
    response = client.klines(symbol, interval, limit=limit)
    return parse_k_lines(response)


# K线数据获取
def get_binance_bars(symbol, interval, startTime, endTime):
    url = "https://api.binance.com/api/v3/klines"
    startTime = str(int(startTime.timestamp() * 1000))
    endTime = str(int(endTime.timestamp() * 1000))
    limit = '50'
    req_params = {"symbol": symbol, 'interval': interval, 'startTime': startTime, 'endTime': endTime, 'limit': limit}
    df = pd.DataFrame(json.loads(requests.get(url, params=req_params).text))
    if (len(df.index) == 0):
        return None
    df = df.iloc[:, 0:6]
    df.columns = ['datetime', 'open', 'high', 'low', 'close', 'volume']
    df.open = df.open.astype("float")
    df.high = df.high.astype("float")
    df.low = df.low.astype("float")
    df.close = df.close.astype("float")
    df.volume = df.volume.astype("float")
    df.index = [dt.datetime.fromtimestamp(x / 1000.0) for x in df.datetime]
    return df


def get_binance_bar_by_start(start_time: dt.datetime):
    df_list = []
    # 数据起点时间
    last_datetime = dt.datetime(2022, 1, 1)
    while True:
        new_df = get_binance_bars('ETHUSDT', '4h', last_datetime, dt.datetime(2022, 7, 10))  # 获取k线数据
        if new_df is None:
            break
        df_list.append(new_df)
        last_datetime = max(new_df.index) + dt.timedelta(0, 5)

    dataframe = pd.concat(df_list)
    dataframe['openinterest'] = 0
    dataframe = dataframe[['open', 'high', 'low', 'close', 'volume', 'openinterest']]
    print(dataframe.shape)
    print(dataframe.tail())
    dataframe.head()


def parse_k_lines(response):
    k_lines = []
    for item in response:
        k_line = []
        # 开盘时间
        timeArray = time.localtime(item[0] / 1000)
        k_line.append(time.strftime('%Y-%m-%d %H:%M:%S', timeArray))
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


def get_history_data(symbol: str, interval: str, start_data=None, end_data=None):
    if start_data is None:
        start_data = dt.datetime(2017, 7, 5)
        end_data = dt.datetime.now()
        data = client.klines(symbol, interval, startTime=str(int(start_data.timestamp() * 1000)),
                             endTime=str(int(end_data.timestamp() * 1000)))
        print(timestamp2str(data[0][0] / 1000))
    if end_data is None:
        end_data = dt.datetime.now()
    df_list = []
    # 数据起点时间
    start_data = dt.datetime(2022, 1, 1)
    while True:
        data = client.klines(symbol, interval, startTime=str(int(start_data.timestamp() * 1000)),
                             endTime=str(int(end_data.timestamp() * 1000)))
        json_data = json.dumps(data, ensure_ascii=False)
        df = pd.DataFrame(json.loads(json_data))
        if len(df.index) == 0:
            break
        df = df.iloc[:, 0:6]
        df.columns = ['datetime', 'open', 'high', 'low', 'close', 'volume']
        df.open = df.open.astype("float")
        df.high = df.high.astype("float")
        df.low = df.low.astype("float")
        df.close = df.close.astype("float")
        df.volume = df.volume.astype("float")
        df.index = [dt.datetime.fromtimestamp(x / 1000.0) for x in df.datetime]

        df_list.append(df)
        start_data = max(df.index) + dt.timedelta(0, 5)
    dataframe = pd.concat(df_list)
    dataframe['openinterest'] = 0
    dataframe = dataframe[['datetime', 'open', 'high', 'low', 'close', 'volume']]
    print(dataframe.shape)
    print(dataframe.tail())
    dataframe.head()

    return dataframe


def k_lines2csv(data, file_name, write_type=None):
    return date2csv(data, file_name, k_lines_csv_head, write_type)


def get_all_history_data(symbol: str, interval: str, start_time=None, end_time=None):
    if start_time is None or end_time is None:
        response = client.klines(symbol, interval)
        start_time = response[0][0]
        end_time = response[len(response) - 1][0]

    file_name = f"{symbol}_{interval}"
    data = []
    while True:
        response = client.klines(symbol, interval, startTime=start_time, endTime=end_time)
        k_lines = parse_k_lines(response)

        if len(k_lines) == 0:
            break

        end_time = response[0][0] - interval_second[interval] * 1000
        start_time = response[0][0] - interval_second[interval] * 1000 * 400
        data.extend(k_lines)

    data.reverse()
    path = k_lines2csv(data, file_name, 'w')
    return path


if __name__ == '__main__':
    file_path = get_all_history_data("OPTUSDT", "1d")


class BiAnService:
    def get_k_line(self, request: GetKLinesRequest):
        k_lines = get_k_lines_by_request(request)
        return k_lines
