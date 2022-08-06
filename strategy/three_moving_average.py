# !/usr/bin389/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
###############################################################################
#
# 该程序基于三根移动线制定策略
#
###############################################################################
from base import *
class ThreeMovingAverage(bt.Strategy):
    params = dict(
        short_period=5,
        median_period=20,
        long_period=60,
        printlog=False)

    def log(self, txt, dt=None, doprint=False):
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print(f'{dt.isoformat()},{txt}')

    def __init__(self):
        self.order = None
        self.close = self.datas[0].close
        self.s_ma = bt.ind.SMA(period=int(self.p.short_period))
        self.m_ma = bt.ind.SMA(period=int(self.p.median_period))
        self.l_ma = bt.ind.SMA(period=int(self.p.long_period))
        # 捕获做多信号
        # 短期均线在中期均线上方，且中期均取也在长期均线上方，三线多头排列，取值为1；反之，取值为0
        self.signal1 = bt.And(self.m_ma > self.l_ma, self.s_ma > self.m_ma)
        # 做多信号，求上面 self.signal1 的环比增量，可以判断得到第一次同时满足上述条件的时间，第一次满足条件为1，其余条件为0
        self.long_signal = bt.If((self.signal1 - self.signal1(-1)) > 0, 1, 0)
        # 做多平仓信号，短期均线下穿长期均线时，取值为1；反之取值为0
        self.close_long_signal = bt.ind.CrossDown(self.s_ma, self.m_ma)
        # 捕获做空信号和平仓信号，与做多相反
        self.signal2 = bt.And(self.m_ma < self.l_ma, self.s_ma < self.m_ma)
        self.short_signal = bt.If((self.signal2 - self.signal2(-1)) > 0, 1, 0)
        self.close_short_signal = bt.ind.CrossUp(self.s_ma, self.m_ma)

    def next(self):
        #         self.log(self.sell_signal[0],doprint=True)
        #         self.log(type(self.position.size),doprint=True)
        # 如果还有订单在执行中，就不做新的仓位调整

        # 如果当前持有多单
        if self.position.size > 0:
            #             self.log(self.position.size,doprint=True)
            # 平仓设置,出现平仓信号进行平仓
            if self.close_long_signal == 1:
                self.order = self.sell(size=abs(self.position.size))
        # 如果当前持有空单
        elif self.position.size < 0:
            # 平仓设置，出现平仓信号进行平仓
            if self.close_short_signal == 1:
                self.order = self.buy(size=abs(self.position.size))
        else:  # 如果没有持仓，等待入场时机
            # 入场: 出现做多信号，做多，开四分之一仓位
            if self.long_signal == 1:
                self.buy_unit = int(self.broker.getcash() / self.close[0] / 4)
                self.order = self.buy(size=self.buy_unit)
            # 入场: 出现做空信号，做空，开四分之一仓位
            elif self.short_signal == 1:
                self.sell_unit = int(self.broker.getcash() / self.close[0] / 4)
                self.order = self.sell(size=self.sell_unit)

    # 打印订单日志
    def notify_order(self, order):
        order_status = ['Created', 'Submitted', 'Accepted', 'Partial',
                        'Completed', 'Canceled', 'Expired', 'Margin', 'Rejected']
        # 未被处理的订单
        if order.status in [order.Submitted, order.Accepted]:
            self.log('ref:%.0f, name: %s, Order: %s' % (order.ref,
                                                        order.data._name,
                                                        order_status[order.status]))
            return
        # 已经处理的订单
        if order.status in [order.Partial, order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, status: %s, ref:%.0f, name: %s, Size: %.2f, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order_status[order.status],  # 订单状态
                     order.ref,  # 订单编号
                     order.data._name,  # 股票名称
                     order.executed.size,  # 成交量
                     order.executed.price,  # 成交价
                     order.executed.value,  # 成交额
                     order.executed.comm))  # 佣金
            else:  # Sell
                self.log(
                    'SELL EXECUTED, status: %s, ref:%.0f, name: %s, Size: %.2f, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order_status[order.status],
                     order.ref,
                     order.data._name,
                     order.executed.size,
                     order.executed.price,
                     order.executed.value,
                     order.executed.comm))

        elif order.status in [order.Canceled, order.Margin, order.Rejected, order.Expired]:
            # 订单未完成
            self.log('ref:%.0f, name: %s, status: %s' % (
                order.ref, order.data._name, order_status[order.status]))

        self.order = None

    def stop(self):
        self.log(
            f'(组合线：{self.p.short_period},{self.p.median_period},{self.p.long_period}); 期末总资金: {self.broker.getvalue():.2f}',
            doprint=False)
