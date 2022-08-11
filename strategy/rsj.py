"""
参考文章
https://mp.weixin.qq.com/s?__biz=MzI1MTQ2Njc5OQ==&mid=2247488152&idx=1&sn=2e5c21624f0046c39a876ad8c5cd771f&scene=21#wechat_redirect
rsj指标策略
RSJ数值越大，则说明未来越倾向于下跌；
RSJ数值越小，则说明未来越倾向于上涨。
"""
import datetime

import numpy
import backtrader

import strategy
from util import data_util


class RsjStrategy(backtrader.Strategy):
    params = dict(
        stop_loss=0.05,
        take_profit=0.1,
        position=0.5,
        validity_day=3,
        expired_day=1000,
    )

    def __init__(self, params=None):
        self.handle_params(params)
        self.order_list = list()

    def handle_params(self, params):
        if params is None:
            return
        if 'stop_loss' in params:
            self.p.stop_loss = params['stop_loss']
        if 'take_profit' in params:
            self.p.stop_loss = params['take_profit']
        if 'position' in params:
            self.p.position = params['position']

        pass

    def get_buy_order(self):
        """
        做多
        :return:
        """
        p1 = self.data.close[0] * (1.0 - self.p.callback)
        p2 = p1 - self.p.stop_loss * p1
        p3 = p1 + self.p.take_profit * p1
        # 计算订单有效期
        validity_day = datetime.timedelta(self.p.validity_day)
        expired_day = valid3 = datetime.timedelta(self.p.expired_day)
        size = min(self.broker.getcash() / self.data.high[0] * self.p.position, self.data.volume)
        orders = self.buy_bracket(size=size,
                                  price=p1, valid=validity_day,
                                  stopprice=p2, stopargs=dict(valid=expired_day),
                                  limitprice=p3, limitargs=dict(valid=valid3), )
        return orders

    def get_sell_order(self):
        """
        做空
        :return:
        """
        p1 = self.data.close[0] * (1.0 - self.p.callback)
        p2 = p1 + self.p.stop_loss * p1
        p3 = p1 - self.p.take_profit * p1
        # 计算订单有效期
        validity_day = datetime.timedelta(self.p.validity_day)
        expired_day = valid3 = datetime.timedelta(self.p.expired_day)
        size = min(self.broker.getcash() / self.data.high[0], self.data.volume)
        orders = self.sell_bracket(size=size,
                                   price=p1, valid=validity_day,
                                   stopprice=p2, stopargs=dict(valid=expired_day),
                                   limitprice=p3, limitargs=dict(valid=valid3), )
        return orders

    def handle_order(self, order):
        if order.status == order.Completed:
            pass
        if not order.alive() and order.ref in self.order_list:
            self.order_list.remove(order.ref)

    def notify_order(self, order):
        self.handle_order(order)

    def buy_sign(self):
        pass

    def sell_sign(self):
        pass

    def close_sign(self):
        pass

    def next(self):
        pass


class TrendBand(backtrader.Indicator):
    lines = ('mid', 'top', 'bot')
    params = (('maperiod', 20),
              ('period', 3),
              ('highRate', 1.2),
              ('lowRate', 0.85),)
    # 与价格在同一张图
    plotinfo = dict(subplot=False)

    def __init__(self):
        ema = backtrader.ind.EMA(self.data, period=self.p.maperiod)
        # 计算上中下轨线
        self.l.mid = backtrader.ind.EMA(ema, period=self.p.period)
        self.l.top = backtrader.ind.EMA(self.mid * self.p.highRate, \
                                        period=self.p.period)
        self.l.bot = backtrader.ind.EMA(self.mid * self.p.lowRate, \
                                        period=self.p.period)
        super(TrendBand, self).__init__()


class DummyInd(backtrader.Indicator):
    # 定义持有的lines，至少需要1个line
    lines = ('dummyline',)

    # params参数可选
    params = (('value', 5),)

    plotinfo = dict(subplot=True)

    # __init__方法或next方法必选
    def __init__(self):
        super(DummyInd, self).__init__()

    def next(self):
        self.lines.dummyline[0] = max(0.0, self.params.value)


class RSJIndicator(backtrader.Indicator):
    """
    RSJ指标
    计算公式：  https://mp.weixin.qq.com/s?__biz=MzI1MTQ2Njc5OQ==&mid=2247488152&idx=1&sn=2e5c21624f0046c39a876ad8c5cd771f&scene=21#wechat_redirect
    """
    # 定义持有的lines，至少需要1个line
    lines = ('rsj',)

    # params参数可选
    params = (('period', 5),
              ('close', None),
              ('open', None),
              ('advance_period', 24),
              )

    plotinfo = dict(subplot=True)

    # __init__方法或next方法必选
    def __init__(self, open_price, close_price, period=15, advance_period=0):
        self.p.open = open_price
        self.p.close = close_price
        self.p.advance_period = advance_period
        self.p.period = period
        print(advance_period)
        super(RSJIndicator, self).__init__()

    def next(self):
        rate_return_list = list()
        for i in range(self.p.advance_period, self.p.advance_period + self.p.period):
            # 计算收益率
            rate = (self.p.open[-i] - self.p.open[-i - 1]) / self.p.open[0] * 100
            rate_return_list.append(rate)
        rv_down = sum(numpy.array([r * r for r in rate_return_list if r < 0]))
        rv_up = sum(numpy.array([r * r for r in rate_return_list if r > 0]))
        rv = sum(numpy.array([r * r for r in rate_return_list]))

        self.lines.rsj[0] = (rv_up - rv_down) / rv
        print(rv_up, rv_down, rv, (rv_up - rv_down) / rv)


class RSJV1Strategy(RsjStrategy):
    """
    具体策略逻辑：
    1.使用5分钟级别的K线来计算RSJ指标；
    2.在每日的14:55计算前一段时间（可调参数）的RSJ指标；
    3.若RSJ指标大于0则发出空头信号，反之则发出多头信号；
    4.基于指标发出的交易信号，在收盘前完成交易（比如14:56）；
    5.持仓到第二天的14:55分，然后重复2-4的步骤调整仓位。
    """

    def __init__(self, params=None):
        super(RSJV1Strategy, self).__init__(params)
        print(self.p.stop_loss)
        self.band = TrendBand()
        self.rsj = RSJIndicator(open_price=self.data.open, close_price=self.data.close, advance_period=24)


if __name__ == '__main__':
    data = data_util.get_local_generic_csv_data('BTC', '1d')
    strategy.run(data, RSJV1Strategy, is_show=True, is_log=True)
