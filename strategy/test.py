from __future__ import (absolute_import, division, print_function, unicode_literals)
import datetime  # 用于datetime对象操作
import os.path  # 用于管理路径
import sys  # 用于在argvTo[0]中找到脚本名称

import backtrader
import backtrader as bt  # 引入backtrader框架

import strategy
from util import data_util


class TS(backtrader.Strategy):
    def __int__(self):
        self.macd = bt.ind.MACD()
        bt.ind.MACDHisto()
        bt.ind.RSI(period=14)
        bt.ind.BollingerBands()


def main():
    data = data_util.get_local_generic_csv_data("ETH", '1h')
    cerebro = strategy.create_cerebro()
    cerebro.adddata(data)
    cerebro.addstrategy(TS)
    cerebro.run()
    cerebro.plot()


if __name__ == '__main__':
    main()
