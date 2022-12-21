"""
交易量突破策略
这是一个失败的策略单烤交易量
"""

from hyperopt import hp

from main.infrastructure.foundation.bt.actuator import *
from main.infrastructure.foundation.bt.optimizer import Optimizer


class VolumeBreakthroughIndex(bt.Indicator):
    lines = (
        'value',
    )
    params = (
        # 放量值
        ('break_volume', 5),
        ('break_ema', 5),

    )  #

    def next(self):
        volume = 0

        for i in range(self.p.break_ema):
            volume += self.data.volume[-i - 2]
        volume = (volume / self.p.break_ema) * self.p.break_volume
        if self.data.volume[0] > volume:
            self.l.value[0] = 1
        else:
            self.l.value[0] = 0
        if self.data.close[0] < self.data.open[0]:
            self.l.value[0] = -1 * self.l.value[0]


class VolumeBreakthroughStrategy(bt.Strategy):
    """
    继承并构建自己的bt策略
    """

    # 定义MA均线策略周期参数变量
    def log(self, txt, dt=None, doprint=False):
        """ 日志函数，用于统一输出日志格式 """
        if doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))

    params = {
        "loss_profit": 3,
        "sell_profit": 3,
        "volume": 1000,
    }

    def __init__(self, params=None):

        if params is not None:
            self.p.loss_profit = params['loss_profit']
            self.p.sell_profit = params["sell_profit"]
            self.p.volume = params["volume"] * 1000
        self.bar_executed = None
        # 初始化相关数据
        self.dataclose = self.datas[0].close
        self.order = None
        self.buyprice = None
        self.buycomm = None

        # 五日移动平均线
        self.sma5 = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=5)
        # 十日移动平均线
        self.sma10 = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=10)
        self.buyprice = 0

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
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            elif order.issell():
                self.log('卖单执行SELL EXECUTED,成交价： %.2f,小计 Cost: %.2f,佣金 Comm %.2f'
                         % (order.executed.price, order.executed.value, order.executed.comm))
                self.buyprice = 0
            self.bar_executed = len(self)

        # 订单因为缺少资金之类的原因被拒绝执行
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # 订单状态处理完成，设为空
        self.order = None

    def notify_trade(self, trade):
        """
        交易成果

        Arguments:
            trade {object} -- 交易状态
        """
        if not trade.isclosed:
            return

        # 显示交易的毛利率和净利润
        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm), doprint=True)

    def next(self):
        """ 下一次执行 """

        # 记录收盘价
        self.log('Close, %.2f' % self.dataclose[0])

        # 是否正在下单，如果是的话不能提交第二次订单
        if self.order:
            return

        # 是否已经买入
        if not self.position:
            # 还没买，如果 MA5 > MA10 说明涨势，买入
            if self.data.volume[-1] > self.p.volume and self.data.close[-1] > self.data.open[-1]:
                self.order = self.buy()
        else:
            profit = (self.data.close[-1] - self.buyprice) / self.buyprice * 100
            if profit > self.p.sell_profit or profit < self.p.loss_profit:
                self.order = self.sell()


if __name__ == '__main__':
    optimizer = Optimizer()
    optimizer.set_date(symbol="ETHUSDT", interval="5m")
    optimizer.set_strategy(VolumeBreakthroughStrategy)
    space = {
        "loss_profit": hp.uniform('loss_profit', 0, 50),
        "sell_profit": hp.uniform('sell_profit', 0, 50),
        "volume": hp.uniform('volume', 10, 1000),
    }
    optimizer.set_space(space)
    params = optimizer.run(1000)


    Actuator.run(strategy=VolumeBreakthroughStrategy, symbol="ETHUSDT", interval='1d', params=params)
