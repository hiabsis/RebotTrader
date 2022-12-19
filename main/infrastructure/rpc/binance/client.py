import datetime
import json
import os
import time

import numpy
import pandas
import requests
from binance.client import Client
from binance.spot import Spot

from main.infrastructure.foundation.logging import log
from main.infrastructure.rpc.binance.dto import QueryKLinesDTO, KLineDTO
from main.infrastructure.rpc.binance.request import QueryLatestFuturesKlinesRequest
from main.infrastructure.utils.bt import BackTradeUtil
from main.infrastructure.utils.date import DateUtil
from main.infrastructure.utils.file import FileUtil
from main.resource.config import PROXIES, KLINES_HEAD

api = Spot(proxies=PROXIES)
query_exchange_info_url = 'https://www.binance.com/fapi/v1/exchangeInfo'

query_feature_k_lines_url = 'https://fapi.binance.v1/fapi'

client = Client()


class BinanceClint(object):

    @staticmethod
    def query_k_lines(request) -> QueryKLinesDTO:
        result = QueryKLinesDTO()
        response = api.klines(request.symbol, request.interval, startTime=request.start, endTime=request.end)
        for res in response:
            k_line = KLineDTO()
            k_line.build(res, request.symbol, request.interval)
            result.data.append(k_line)
        return result

    @staticmethod
    def query_symbols(currency='USDT'):
        symbols = []
        response = requests.get(
            url=query_exchange_info_url,
            proxies=PROXIES
        )

        data = json.loads(response.content.decode("utf-8"))['symbols']
        for d in data:
            symbol = d['symbol']
            if symbol[-4:] == currency:
                symbols.append(symbol)
        return symbols

    @staticmethod
    def query_feature_latest_klines(request: QueryLatestFuturesKlinesRequest):
        result = QueryKLinesDTO()
        try:
            response = client.futures_klines(symbol=request.symbol, interval=request.interval, startTime=request.start,
                                             endTime=request.end)
        except Exception as e:
            log.error("请求失败,无法获取合约数据 由于{}".format(str(e)))
            result.is_success = False
            return result
        for res in response:
            k_line = KLineDTO()
            k_line.build(res, request.symbol, request.interval)
            result.data.append(k_line)
        return result

    @staticmethod
    def download_kline(symbol, interval):
        log.info("下载K线  {} {}".format(symbol, interval))
        file_path = BackTradeUtil.local_path(symbol, interval)
        file_path = '/'.join(file_path.split('\\'))
        log.info("数据保存位置 {}".format(file_path))
        if os.path.exists(file_path):
            data = numpy.array(pandas.read_csv(file_path))
            start = DateUtil.str2datetime(data[-1][0])
            start = DateUtil.add_time(start, minutes=int(DateUtil.interval2second(interval) / 60))
            end = DateUtil.add_time(start, minutes=int(DateUtil.interval2second(interval) / 60) * 100)
            start = int(time.mktime(start.timetuple())) * 1000
            end = int(time.mktime(end.timetuple())) * 1000
            if end >= int(time.mktime(datetime.datetime.now().timetuple())) * 1000:
                end = int(time.mktime(datetime.datetime.now().timetuple())) * 1000
            if end <= start:
                return
            klines = []
            while True:
                response = client.futures_klines(symbol=symbol, interval=interval, startTime=start,
                                                 endTime=end)
                for res in response:
                    k_line = KLineDTO()
                    k_line.build(res, symbol, interval)
                    klines.append(
                        [k_line.open_time, k_line.open_price, k_line.close_price, k_line.high_price, k_line.close_price,
                         k_line.volume])
                if response is None or response == [] or end >= int(
                        time.mktime(datetime.datetime.now().timetuple())) * 1000:
                    break
                end = response[0][0] + DateUtil.interval2second(interval) * 1000
                start = response[0][0] + DateUtil.interval2second(interval) * 1000 * 300
                log.info("下载 {}".format(klines[-1][0]))
            FileUtil.data2csv(klines, KLINES_HEAD, file_path, 'a')
        else:

            end = datetime.datetime.now()
            start = DateUtil.add_second(-1 * 300 * DateUtil.interval2second(interval), end)
            start = int(time.mktime(start.timetuple())) * 1000
            end = int(time.mktime(end.timetuple())) * 1000
            klines = []
            while True:
                response = client.futures_klines(symbol=symbol, interval=interval, startTime=start,
                                                 endTime=end)
                size = len(response)
                for i in range(size):
                    res = response[size - i - 1]
                    k_line = KLineDTO()
                    k_line.build(res, symbol, interval)
                    klines.append(
                        [k_line.open_time, k_line.open_price, k_line.close_price, k_line.high_price, k_line.close_price,
                         k_line.volume])
                if response is None or response == []:
                    break
                end = response[0][0] - DateUtil.interval2second(interval) * 1000
                start = response[0][0] - DateUtil.interval2second(interval) * 1000 * 300
                log.info("下载 {} {}".format(symbol, klines[-1][0]))

            klines.reverse()
            FileUtil.data2csv(klines, KLINES_HEAD, file_path)


if __name__ == '__main__':
    BinanceClint.download_kline("DOTUSDT", "5m")
