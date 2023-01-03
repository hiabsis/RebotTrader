"""
垃圾指标 一言难尽
"""
import datetime
import math

from hyperopt import hp

from main.infrastructure.foundation.bt.actuator import *
from main.infrastructure.foundation.bt.optimizer import Optimizer
from main.infrastructure.utils.math import MathUtil
from main.resource.config import ENABLE_STRATEGY_LOG


class ObvIndex(bt.Indicator):
    lines = (
        'value',
    )
    params = {
        "period": 30,

    }

    def __init__(self, data, period=30):
        self.data = data
        self.p.period = period
        self.volume = 0
        self.xi = []
        self.yi = []

        for i in range(self.p.period):
            self.xi.append(i + 1)
            self.yi.append(0)

    def next(self):
        self.avg_value()
        self.yi.pop(0)
        self.yi.append(self.volume)
        k, b = MathUtil.least_square_method(self.xi, self.yi)
        if k > 0:
            self.l.value[0] = 1
        elif k == 0:
            self.l.value[0] = 0
        else:
            self.l.value[0] = -1

    def avg_value(self):

        if not math.isnan(self.data[-self.p.period]):
            self.volume = self.volume - self.data[-self.p.period] + self.data[0]
        else:
            self.volume = self.volume - self.data[-self.p.period] + self.data[0]


class SmaRsJ(bt.Indicator):
    lines = (
        'value',
        'highest',
        'lowest',

    )

    def __init__(self, period=20):
        self.l.value = bt.ind.SMA(bt.ind.RSI(), period=period)
        self.l.highest = bt.ind.Highest(self.l.value, period=period * 5)
        self.l.lowest = bt.ind.Lowest(self.l.value, period=period * 5)


class TestStrategy(bt.Strategy):
    params = dict(
        period=30,
        buy_rsi=30,
        sell_rsi=70
    )

    def __init__(self, params=None):
        self.order = None
        self.log("params : {}".format(params))
        if params is not None:
            self.p.period = params['period']
            self.p.buy_rsi = params['buy_rsi']
            self.p.sell_rsi = params['sell_rsi']
        rsj = SmaRsJ()
        self.rsj = rsj.value
        self.rsj_highest = rsj.highest
        self.rsj_lowest = rsj.lowest
        self.add_timer(
            when=datetime.time(8, 0),
            weekdays=[1, 3, 5, 7],
            monthcarry=True,
        )

    def notify_timer(self, timer, when, *args, **kwargs):

        self.rebalance_portfolio()  # 执行再平衡def notify_timer(self, timer, when, *args, **kwargs):

    def log(self, txt, dt=None):
        """ 日志函数，用于统一输出日志格式 """

        if ENABLE_STRATEGY_LOG:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))

    def notify_order(self, order):
        """
        订单状态处理
        Arguments:
            order {object} -- 订单状态
        """
        if order.status in [order.Submitted, order.Accepted]:
            # 如订单已被处理，则不用做任何事情
            return

        # 检查订单是否完成
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('买单执行BUY EXECUTED,成交价： %.2f,小计 Cost: %.2f,佣金 Comm %.2f'
                         % (order.executed.price, order.executed.value, order.executed.comm))

            elif order.issell():
                self.log('卖单执行SELL EXECUTED,成交价： %.2f,小计 Cost: %.2f,佣金 Comm %.2f'
                         % (order.executed.price, order.executed.value, order.executed.comm))


        # 订单因为缺少资金之类的原因被拒绝执行
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # 订单状态处理完成，设为空
        self.order = None

    def notify_trade(self, trade):
        if trade.isclosed:
            self.log('毛收益 %0.2f, 扣佣后收益 % 0.2f, 佣金 %.2f, 市值 %.2f, 现金 %.2f' %
                     (trade.pnl, trade.pnlcomm, trade.commission, self.broker.getvalue(), self.broker.getcash()))

    def rebalance_portfolio(self):
        # self.close()
        # 是否已经买入
        if self.rsj[0] <= self.p.buy_rsi + self.rsj_lowest[0]:
            target = int(self.broker.getcash() / 10)
            self.order_target_value(target=target)
        if self.rsj[0] >= self.rsj_lowest[0] - self.p.sell_rsi > self.p.sell_rsi and self.position is not None:
            self.close()


interval = "4h"
symbol = "BNBUSDT"
start = "2021-01-01 00:00:00"
end = "2022-12-21 00:00:00"


# cerebro = Actuator.run(TestStrategy, symbol=symbol, interval=interval, start_time=start, end_time=end, plot=False)


def optimizer():
    space = dict(
        period=hp.uniform("period", 0, 50),
        buy_rsi=hp.uniform("buy_rsi", 0, 50),
        sell_rsi=hp.uniform("sell_rsi", 0, 50)
    )
    op = Optimizer()
    op.set_date(symbol=symbol, interval=interval, start_time=start, end_time=end)
    op.set_space(space)
    op.set_strategy(TestStrategy)
    return op.run(evals=100)


params = {'buy_rsi': 1.0498577868035641, 'period': 25, 'sell_rsi': 29.2583301692514}
params = {'buy_rsi': 1, 'period': 14.27557713839837, 'sell_rsi': 30}
# cerebro = Actuator.run(TestStrategy, symbol=symbol, interval=interval, start_time=start, end_time=end, plot=True,
#                        params=params)
# Analyzer.pyfolio(cerebro, "{}-{}".format(symbol, interval))
# params = optimizer()
symbols = BinanceClint.query_symbols()
for symbol in symbols:
    cerebro = Actuator.run(TestStrategy, symbol=symbol, interval=interval, start_time=start, end_time=end, plot=False,
                           params=params)
    