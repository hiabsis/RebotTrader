import backtrader as bt

from main.resource.config import KLINES_PATH


class BackTradeUtil:
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

        if interval is None:
            interval_type = bt.TimeFrame.Minutes
        elif interval.endswith('d'):
            interval_type = bt.TimeFrame.Days
        else:
            interval_type = bt.TimeFrame.Minutes

        return bt.feeds.GenericCSVData(
            dataname=path,
            nullvalue=0.0,
            fromdate=start,
            todate=end,
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
