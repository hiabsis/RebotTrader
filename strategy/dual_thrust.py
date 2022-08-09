import datetime

import hyperopt.hp

from strategy import *


class DualThrustStrategy(bt.Strategy):
    """
    具体计算过程如下：
    N日High的最高价HH, 日High的最低价LC;
    N日Close的最高价HC，N日Low的最低价LL;
    Range = Max(HH-LC,HC-LL)
    上轨(upperLine )= Open + K1*Range
    下轨(lowerLine )= Open + K2*Range
    突破上轨做多，跌破下轨翻空
    原文链接：https://blog.csdn.net/lianshaohua/article/details/112213357
    """
    params = dict(
        period=24,
        h_period=30,
        l_period=30,
        k1=0.1,
        k2=0.1,
        is_log=False
    )

    def log(self, txt, dt=None):
        if self.p.is_log:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s,%s' % (dt.isoformat(), txt))

    def __init__(self):

        hh = bt.indicators.Highest(self.data.high, period=self.p.h_period * self.p.period)
        lc = bt.indicators.Lowest(self.data.high, period=self.p.l_period * self.p.period)
        hc = bt.indicators.Highest(self.data.close, period=self.p.h_period * self.p.period)
        ll = bt.indicators.Highest(self.data.close, period=self.p.l_period * self.p.period)
        r = bt.Max(hh - lc, hc - ll)

        self.top = self.data.open + self.p.k1 * r
        # 下轨
        self.bot = self.data.open - self.p.k2 * r

        # 记录交易订单
        self.order = None

    def get_buy_unit(self):
        """
        每次交易购买的数量
        :return:
        """
        size = self.broker.getcash() / self.data.high[0] * 0.25
        if size == 0:
            size = 1
        return int(size)

    def next(self):
        # # 如果订单为处理完成 继续处理
        if self.order:
            return
        size = self.get_buy_unit()
        # 没有持有仓位
        if not self.position:

            if self.data.high[0] > self.top[-self.p.period]:
                self.order = self.buy(size=size)  # 买入
            if self.data.open[0] > self.bot[-1]:
                self.order = self.sell(size=size)

        elif self.position.size > 0:
            # 在多头情况下，平仓条件
            if self.data.open[0] < self.bot[-self.p.period]:
                # 最新价低于中线，多头清仓离场
                self.close()
                self.order = self.sell(size=size)

        elif self.position.size < 0:
            # 在空头情况下，平仓条件
            if self.data.open[0] > self.top[-1]:
                # 最新价高于中线，空头清仓离场
                self.close()
                self.order = self.buy(size=size)
        pass

    def notify(self, order):
        if order.status in [order.Completed, order.Canceled, order.Margin]:
            if order.isbuy():
                self.log('执行买入, %.2f' % order.executed.price)
                self.order = None
            elif order.issell():
                self.log('执行卖出, %.2f' % order.executed.price)
                self.order = None


def create_dual_thrust_strategy(params=None):
    c = create_cerebro()
    if params is None:
        c.addstrategy(DualThrustStrategy)
    else:
        c.addstrategy(DualThrustStrategy,
                      period=int(params['period']),
                      h_period=int(params['h_period']),
                      l_period=int(params['l_period']),
                      k1=params['k1'],
                      k2=params['k2'],
                      )
    return c


if __name__ == '__main__':
    data = data_util.get_local_generic_csv_data('ENSUSDT', '1h')
    run_strategy(create_dual_thrust_strategy, data, {
        "h_period": 10.227848382187478,
        "k1": 0.432033810690125,
        "k2": 1.5620706927069408,
        "l_period": 34.85264244259156,
        "period": 6.409045290050317
    },is_show=True)
    # space = dict(
    #     period=hp.uniform('period', 1, 10),
    #     h_period=hp.uniform('h_period', 1, 36),
    #     l_period=hp.uniform('l_period', 1, 36),
    #     k1=hp.uniform('k1', 0, 2),
    #     k2=hp.uniform('k2', 0, 2),
    # )
    # opt = Optimizer(create_strategy_func=create_dual_thrust_strategy, space=space, max_evals=500, data=data,
    #                 is_send_ding_task=True)
    # p = opt.run()
    # opt.plot()
    # analyze_strategy(data, create_dual_thrust_strategy, p, is_show=True)
