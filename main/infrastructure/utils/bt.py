import os

import backtrader as bt

from main.infrastructure.foundation.logging import log
from main.infrastructure.utils.date import DateUtil
from main.resource.config import KLINES_PATH, ANALYZE_PATH


class BackTradeUtil:
    @staticmethod
    def analyzer_path(out):
        save_dir = "{}".format(ANALYZE_PATH)
        file_path = "{}/{}.html".format(save_dir, out)
        print(save_dir)
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        with open(file_path, 'w', encoding='utf-8') as f:
            print(f)
        return file_path

    @staticmethod
    def local_path(symbol, interval):
        return "{}/{}/{}.csv".format(KLINES_PATH, symbol, interval)

    @staticmethod
    def load_csv(symbol, interval: str, start=None, end=None, ):
        """
        时间级别
        :param symbol:
        :param start:
        :param end:
        :param interval:
        :return:
        """
        path = BackTradeUtil.local_path(symbol, interval)
        log.info("加载 {} {}".format(symbol, interval))
        if interval is None:
            interval_type = bt.TimeFrame.Minutes
        elif interval.endswith('d'):
            interval_type = bt.TimeFrame.Days
        else:
            interval_type = bt.TimeFrame.Minutes

        return bt.feeds.GenericCSVData(
            dataname=path,
            nullvalue=0.0,
            fromdate=DateUtil.str2datetime(start),
            todate=DateUtil.str2datetime(end),
            dtformat="%Y-%m-%d %H:%M:%S",
            timeframe=interval_type,
            datetime=0,
            high=3,
            low=4,
            open=1,
            close=2,
            volume=5,
            openinterest=-1
        )
