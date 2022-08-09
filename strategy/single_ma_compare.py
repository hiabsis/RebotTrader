"""
单移动线的对比
"""
import datetime

import strategy
import backtrader

from indicator.ema import EmaBandIndicator
from strategy.test import St
from util import data_util


class SingleStrategy(backtrader.Strategy):
    params = dict(
        period=30,
        stop_loss=0.05,  # 止损比例
        take_profit=0.1,  # 止盈比例
        validity_day=3,  # 订单有效期
        expired_day=1000,  # 订单失效期
    )

    def get_order(self):
        p1 = self.dataclose[0] * (1.0 - self.p.callback)
        p2 = p1 - self.p.stop_loss * p1
        p3 = p1 + self.p.take_profit * p1
        # 计算订单有效期
        validity_day = datetime.timedelta(self.p.validity_day)
        expired_day = valid3 = datetime.timedelta(self.p.expired_day)
        size = min(self.broker.getcash() / self.data.high[0], self.data.volume)
        orders = self.buy_bracket(size=size,
                                  price=p1, valid=validity_day,
                                  stopprice=p2, stopargs=dict(valid=expired_day),
                                  limitprice=p3, limitargs=dict(valid=valid3), )
        return orders


class KAMASingleStrategy(SingleStrategy):

    def __int__(self):
        self.buy_sig = NegativeIndicator().buy_sig
        # self.kama = backtrader.talib.KAMA(self.data.close, timeperiod=self.p.period)
        # self.kama2 = EmaBandIndicator()
        self.kama2 = KAMAIndicator()


class NegativeIndicator(backtrader.Indicator):
    lines = ('buy_sig',)



    params = (('ma_period ', 10), ('up_period', 3))

    def __init__(self):
        self.addminperiod(self.p.ma_period)
        ma = backtrader.ind.SMA(period=self.p.ma_period, plot=True)
        # 买入条件
        # 收阴线
        self.l.buy_sig = backtrader.And(self.data.close < self.data.open,
                                        # 收在均线上方
                                        self.data.close > ma,
                                        # 均线向上
                                        ma == backtrader.ind.Highest(ma, period=self.p.up_period)
                                        )


def create_kama_single_strategy(params):
    c = strategy.create_cerebro()
    if params is None:
        c.addstrategy(KAMASingleStrategy)
    else:
        c.addstrategy(KAMASingleStrategy,
                      period=int(params['period']))
    return c


class KAMAIndicator(backtrader.Indicator):
    """
    ema通道
        mid = ema(ema(price,rend_period)
        top = ema(ema(price,rend_period)
        bot = ema(ema(price,rend_period)
    """
    lines = ('value',)
    params = (
        ('period', 30),
    )
    # # 与价格在同一张图
    # plotinfo = dict(subplot=False)

    def __init__(self):
        self.l.value = backtrader.talib.KAMA(self.data.close, timeperiod=self.p.period)
        super(KAMAIndicator, self).__init__()


if __name__ == '__main__':
    data = data_util.get_local_generic_csv_data("ETH", '1h')
    cerebro = backtrader.Cerebro()  # 创建cerebro
    # 先找到脚本的位置，然后根据脚本与数据的相对路径关系找到数据位置
    # 这样脚本从任意地方被调用，都可以正确地访问到数据
    cerebro.adddata(data)
    # 设置启动资金
    cerebro.broker.setcash(100000.0)
    # 设置交易单位大小
    cerebro.addsizer(backtrader.sizers.FixedSize, stake=1000)
    # 设置佣金为千分之一
    cerebro.broker.setcommission(commission=0.001)
    cerebro.addstrategy(KAMASingleStrategy)  # 添加策略
    cerebro.run()  # 遍历所有数据
    # 打印最后结果
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro.plot(style='candlestick')
