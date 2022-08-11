import datetime

import backtrader
import numpy
from hyperopt import hp

import strategy
from util import data_util, math_util


def create_art(params=None):
    return strategy.create_strategy(AtrStrategy, params)


def create_dynamic_art(params=None):
    return strategy.create_strategy(DynamicAtrStrategy, params)


def create_continue_down_atr_strategy(params=None):
    return strategy.create_strategy(ContinueDownAtrStrategy, params)


def create_dynamic_atr_strategy_v2(params):
    return strategy.create_strategy(DynamicAtrStrategyV2, params)


class AtrStrategy(backtrader.Strategy):
    params = dict(
        art_period=14,
        art_low=5,
        callback=0.01,
        stop_loss=0.05,
        position=0.5,
        take_profit=0.1,
        validity_day=3,
        expired_day=1000,
        atr_low=10,
        atr_high=100
    )

    def __init__(self, params=None):
        self.handle_params(params)
        self.atr = backtrader.indicators.ATR(period=self.p.art_period)
        self.ema = backtrader.indicators.EMA()
        self.order_list = list()

    def handle_params(self, params):
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

    def buy_sing(self):
        # 获取前六天的数据
        ema_list = self.get(ago=6, size=3)
        # 创建点
        x = []
        y = []
        for i in range(3):
            x.append(i)
            y.append(self.ema[-i])
            y.reverse()
        xi = numpy.array(x)
        yi = numpy.array(y)
        # 计算斜率
        k, b = math_util.least_squares_lines(xi, yi)
        if k > 0.2:
            return False
        # atr 值

    def next(self):

        if self.order_list:
            return

        if self.atr[0] < self.atr[-1] < self.atr[-2] and self.atr[0] < self.p.art_low:
            orders = self.get_buy_order()
            # 保存激活的的订单
            self.order_list = [o.ref for o in orders]


class DynamicAtrStrategy(AtrStrategy):
    """
    测试数据
    "数据源":"D:\\work\\git\\RebotTrader\\static\\data\\ETHUSDT_1h.csv",
    "收益率":"96516.6237312468 %",
    "参数":{
        "art_lowest_period":95.28260781970545,
        "art_period":64.02704141236504,
        "position":0.9995364843544763,
        "stop_loss":0.5121362175837294,
        "take_profit":0.3560544958062028
    }
    动态调整低点
    """
    params = dict(
        art_period=14,
        art_lowest_period=10,
        art_low=5,
        callback=0.01,
        stop_loss=0.05,
        position=0.5,
        take_profit=0.1,
        validity_day=3,
        expired_day=1000,
        atr_low=10,
        atr_high=100
    )

    def __init__(self, params=None):
        self.handle_params(params)
        self.atr = backtrader.indicators.ATR(period=self.p.art_period)
        self.ema = backtrader.indicators.EMA()
        self.ema_atr = backtrader.indicators.EMA(self.atr, period=self.p.art_period)
        self.order_list = list()
        self.art_lowest = backtrader.indicators.Lowest(self.atr, period=self.p.art_lowest_period)

    def handle_params(self, params):
        if 'art_period' in params:
            self.p.art_period = int(params['art_period'])
        if 'stop_loss' in params:
            self.p.stop_loss = params['stop_loss']
        if 'take_profit' in params:
            self.p.stop_loss = params['take_profit']
        if 'position' in params:
            self.p.position = params['position']
        if 'art_lowest_period' in params:
            self.p.art_lowest_period = int(params['art_lowest_period'])

        pass

    def next(self):

        if self.order_list:
            return
        if self.atr[0] < self.atr[-1] < self.atr[-2] and self.atr[0] < self.art_lowest[-5]:
            orders = self.get_buy_order()
            # 保存激活的的订单
            self.order_list = [o.ref for o in orders]


class DynamicAtrStrategyV2(AtrStrategy):
    """
    再版本二中加入做空策略
    """
    params = dict(
        art_period=14,
        art_down_period=3,
        art_up_period=3,
        callback=0.01,
        stop_loss=0.05,
        position=0.5,
        take_profit=0.1,
        validity_day=3,
        expired_day=1000,
        atr_low=10,
        atr_high=100
    )

    def __init__(self, params=None):
        self.handle_params(params)
        self.atr = backtrader.indicators.ATR(period=self.p.art_period)
        self.art_lowest = backtrader.indicators.Lowest(self.atr, period=self.p.art_down_period)
        self.art_highest = backtrader.indicators.Highest(self.atr, period=self.p.art_up_period)
        self.order_list = list()

    def handle_params(self, params):
        if params is None:
            return
        if 'art_period' in params:
            self.p.art_period = int(params['art_period'])
        if 'art_down_period' in params:
            self.p.art_down_period = int(params['art_down_period'])
        if 'art_up_period' in params:
            self.p.art_up_period = int(params['art_up_period'])
        if 'stop_loss' in params:
            self.p.stop_loss = params['stop_loss']
        if 'take_profit' in params:
            self.p.stop_loss = params['take_profit']
        if 'position' in params:
            self.p.position = params['position']
        pass

    def next(self):

        if self.order_list:
            return
        art_list = []
        for i in range(self.p.art_down_period):
            art_list.append(self.atr[-i])
            art_list.reverse()

        if self.atr[0] < self.atr[-1] < self.atr[-2] and self.atr[0] < self.art_lowest[-5]:
            orders = self.get_buy_order()
            # 保存激活的的订单
            self.order_list = [o.ref for o in orders]

        if self.atr[-2] < self.atr[-1] < self.atr[0] < self.art_highest[-5]:
            orders = self.get_sell_order()
            # 保存激活的的订单
            self.order_list = [o.ref for o in orders]


class ContinueDownAtrStrategy(AtrStrategy):
    params = dict(
        art_period=14,
        art_down_period=3,
        callback=0.01,
        stop_loss=0.05,
        position=0.5,
        take_profit=0.1,
        validity_day=3,
        expired_day=1000,
        atr_low=10,
        atr_high=100
    )

    def __init__(self, params=None):
        self.handle_params(params)
        self.atr = backtrader.indicators.ATR(period=self.p.art_period)
        self.ema = backtrader.indicators.EMA()
        self.order_list = list()

    def handle_params(self, params):
        if 'art_period' in params:
            self.p.art_period = int(params['art_period'])
        if 'art_down_period' in params:
            self.p.art_down_period = int(params['art_down_period'])
        if 'stop_loss' in params:
            self.p.stop_loss = params['stop_loss']
        if 'take_profit' in params:
            self.p.stop_loss = params['take_profit']
        if 'position' in params:
            self.p.position = params['position']

        pass

    def next(self):

        if self.order_list:
            return
        art_list = []
        for i in range(self.p.art_down_period):
            art_list.append(self.atr[-i])
            art_list.reverse()

        if art_list == sorted(art_list, reverse=True):
            orders = self.get_buy_order()
            # 保存激活的的订单
            self.order_list = [o.ref for o in orders]


if __name__ == '__main__':
    data = data_util.get_local_generic_csv_data('BTC', '1h')
