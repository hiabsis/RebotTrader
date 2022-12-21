import math

from hyperopt import hp

from main.infrastructure.foundation.bt.actuator import *
from main.infrastructure.foundation.bt.optimizer import Optimizer
from main.infrastructure.utils.math import MathUtil


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

    def log(self, txt, dt=None, doprint=False):
        """ 日志函数，用于统一输出日志格式 """

        if doprint:
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

    def next(self):
        """ 下一次执行 """

        # 记录收盘价
        # 是否正在下单，如果是的话不能提交第二次订单
        if self.order:
            return

        # 是否已经买入
        if not self.position and self.rsj[0] <= self.p.buy_rsi + self.rsj_lowest[0]:
            self.order = self.buy()
        if self.rsj[0] >= self.p.sell_rsi + self.rsj_lowest[0] > self.p.sell_rsi and self.position:
            self.close()
            self.order = None


interval = "4h"
symbol = "ETHUSDT"
start = "2020-01-01 00:00:00"
end = "2022-12-21 00:00:00"


# cerebro = Actuator.run(TestStrategy, symbol=symbol, interval=interval, start_time=start, end_time=end, plot=False)


def optimizer():
    space = dict(
        period=hp.uniform("period", 0, 50),
        buy_rsi=hp.uniform("buy_rsi", 0, 30),
        sell_rsi=hp.uniform("sell_rsi", 0, 30)
    )
    op = Optimizer()
    op.set_date(symbol=symbol, interval=interval, start_time=start, end_time=end)
    op.set_space(space)
    op.set_strategy(TestStrategy)
    return op.run(evals=3000)


params = {'buy_rsi': 5, 'period': 35, 'sell_rsi': 5}
# cerebro = Actuator.run(TestStrategy, symbol=symbol, interval=interval, start_time=start, end_time=end, plot=True,
#                        params=params)
# Analyzer.pyfolio(cerebro, "{}-{}".format(symbol, interval))
params = optimizer()
cerebro = Actuator.run(TestStrategy, symbol=symbol, interval=interval, start_time=start, end_time=end, plot=True,
                       params=params)
