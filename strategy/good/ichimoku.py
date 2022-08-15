import datetime
import logging
import math

import numpy

import strategy.good.art as art
import backtrader
import util
import actuator
import analyze
from util.math_util import least_squares_lines


class IchimokuStrategy(backtrader.Strategy):
    params = dict(
        stop_loss=0.05,
        take_profit=0.1,
        position=0.5,
        validity_day=3,
        expired_day=1000,
    )

    def to_buy(self):
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

    def to_sell(self):
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

    def next(self):
        pass


class IchimokuV1Strategy(backtrader.Strategy):
    """
    版本一:
    做多
    1、K线在云层上方；
    2、转换线从下往上穿过基准线与其云层上方
    """
    params = dict(
        tenkan_sen_period=20,
        senkou_span_a_pre=26,
        senkou_span_b_pre=80,
        senkou_span_b_period=100,
        kijun_sen_period=50,
        callback=0.02,
        stop_loss=0.05,
        take_profit=0.1,
        position=0.5,
        validity_day=3,
        expired_day=1000,
    )

    def handle_params(self, params):
        if params is None:
            return
        if 'art_period' in params:
            self.p.art_period = int(params['art_period'])
        if 'art_low' in params:
            self.p.art_low = params['art_low']
        if 'stop_loss' in params:
            self.p.stop_loss = params['stop_loss']
        if 'take_profit' in params:
            self.p.stop_loss = params['take_profit']
        if 'position' in params:
            self.p.position = params['position']
        if 'tenkan_sen_period' in params:
            self.p.tenkan_sen_period = params['tenkan_sen_period']
        if 'senkou_span_a_pre' in params:
            self.p.tenkan_sen_period = params['senkou_span_a_pre']
        if 'senkou_span_a_pre' in params:
            self.p.tenkan_sen_period = params['senkou_span_a_pre']

        if 'senkou_span_b_pre' in params:
            self.p.senkou_span_b_pre = params['senkou_span_b_pre']
        if 'senkou_span_b_period' in params:
            self.p.senkou_span_b_period = params['senkou_span_b_period']
        pass

    def __init__(self, params=None):

        ichimoku = IchimokuIndicator(line_plot=[False, False, True, True])
        self.kijun_sen = ichimoku.kijun_sen
        self.tenkan_sen = ichimoku.tenkan_sen
        self.senkou_span_b = ichimoku.senkou_span_b
        self.senkou_span_a = ichimoku.senkou_span_a
        self.order = None

        self.crossover = backtrader.ind.CrossOver(self.senkou_span_a, self.senkou_span_b)

    def notify_order(self, order):
        if order.status in [order.Completed, order.Canceled, order.Margin]:
            if order.isbuy():
                self.order = None
            elif order.issell():
                self.order = None

    def to_buy(self):
        """
        做多
        :return:
        """

        size = min(int(self.broker.getcash() / self.data.high[0] * self.p.position), self.data.volume)
        self.order = self.buy(size=size, price=self.data.close[0] * (1 - self.p.callback))

    def to_sell(self):
        """
        做空
        :return:
        """
        size = min(int(self.broker.getcash() / self.data.high[0] * self.p.position), self.data.volume)
        self.order = self.sell(size=size, price=self.data.close[0] * (1 + self.p.callback))

    def buy_sign(self):

        if self.crossover[0] > 0:
            return True
        return False

    def sell_sign(self):

        if self.crossover[0] < 0:
            return True
        return False

    def next(self):
        if math.isnan(self.senkou_span_a[-15]):
            return

        if self.order:
            return

        if not self.position:
            if self.buy_sign():
                self.to_buy()
            # if self.sell_sign():
            #     self.to_sell()

        if self.position.size > 0:
            if self.sell_sign():
                self.close()

        # if self.position.size < 0:
        #     if self.buy_sign():
        #         self.close()


def _dy_period(min_length, max_length, para=True, adapt_pct=0.968):
    dyna_len = (min_length + max_length) / 2
    if para:
        dyna_len = max(min_length, dyna_len * adapt_pct)
    else:
        dyna_len = max(min_length, dyna_len * (2 - adapt_pct))
    return dyna_len


class IchimokuIndicator(backtrader.Indicator):
    """
    一目均衡表指标
    tenkan-sen（转换线）：即多空反转信号线。
    转换线算法：过去9日最高的最高价加上最低的最低价的和，除以2来计算。
    公式：（9日内最高价+9日内最低价）/2

    kijun-sen（基线）：即多空趋势变化，可用作追踪止损点。
    基线算法：过去26日最高的最高价加上最低的最低价的和，除以2来计算。
    公式：（26日内最高价+26日内最低价）/2

    senkou span A（跨度A）：即云顶。
    跨度A算法：转换线与基线之和再除以2，然后将结果绘制在前面26个周期来计算。
    公式：（转换线的值+基线的值）/2

    senkou span B（跨度B）：即云底。
    跨度B算法：最高价与最低价的和除以2，然后将结果绘制在前面52个周期来计算。
    公式：（52日最高价+52日最低价）/2

    chikou span（延迟线）：用于显示支撑和压力区域。
    延迟线算法：以当日为第一天算起，第26日的收盘价。
    """
    lines = ('tenkan_sen', 'kijun_sen', 'senkou_span_a', 'senkou_span_b',)
    params = (
        ('tenkan_sen_period', 20),
        ('kijun_sen_period', 50),
        ('senkou_span_a_pre', 26),
        ('senkou_span_b_pre', 80),
        ('senkou_span_b_period', 100),
        ('line_plot', [True, True, True, True]),
    )

    plotinfo = dict(subplot=False)

    def __init__(self):

        # # 最高价
        tenkan_sen_highest = backtrader.ind.Highest(self.data.high, period=self.p.tenkan_sen_period)
        tenkan_sen_lowest = backtrader.ind.Lowest(self.data.low, period=self.p.tenkan_sen_period)
        self.tenkan_sen_temp = backtrader.indicators.Average((tenkan_sen_highest + tenkan_sen_lowest) / 2,
                                                             period=self.p.tenkan_sen_period, )
        if self.p.line_plot[0]:
            # 转换线
            self.l.tenkan_sen = self.tenkan_sen_temp

        kijun_sen_highest = backtrader.ind.Highest(self.data.high, period=self.p.kijun_sen_period)
        kijun_sen_lowest = backtrader.ind.Lowest(self.data.high, period=self.p.kijun_sen_period)
        self.kijun_sen_temp = backtrader.ind.Average((kijun_sen_lowest + kijun_sen_highest) / 2,

                                                     period=self.p.kijun_sen_period)
        if self.p.line_plot[1]:
            self.l.kijun_sen = self.kijun_sen_temp

        super(IchimokuIndicator, self).__init__()

    def next(self):
        if self.p.line_plot[2]:
            self.l.senkou_span_a[0] = (self.tenkan_sen_temp[-self.p.senkou_span_a_pre] + self.kijun_sen_temp[
                -self.p.senkou_span_a_pre]) / 2
        if self.p.line_plot[3]:
            highest = 0
            lowest = 1000 * 1000 * 1000
            for i in range(0, int(self.p.senkou_span_b_period)):
                if highest < self.data.high[-i - self.p.senkou_span_b_pre]:
                    highest = self.data.high[-i - self.p.senkou_span_b_pre]
                if lowest > self.data.low[-i - self.p.senkou_span_b_pre]:
                    lowest = self.data.low[-i - self.p.senkou_span_b_pre]
            self.l.senkou_span_b[0] = (highest + lowest) / 2
        pass


if __name__ == '__main__':
    actuator.batch_run(IchimokuV1Strategy)
