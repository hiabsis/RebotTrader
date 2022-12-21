"""
组合策略
"""
import backtrader as bt

from main.infrastructure.foundation.logging import log

class MuOBVStrategy(bt.Strategy):
    params = dict(
        period=30,
        num=30
    )

    def log(self, txt, dt=None, doprint=True):
        """ 日志函数，用于统一输出日志格式 """

        if doprint:
            dt = dt or self.datas[0].datetime.date(0)
            log.info('%s, %s' % (dt.isoformat(), txt))

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # 订单状态 submitted/accepted，无动作
            return

        # 订单完成
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('买单执行,%s, %.2f, %i' % (order.data._name,
                                                    order.executed.price, order.executed.size))

            elif order.issell():
                self.log('卖单执行, %s, %.2f, %i' % (order.data._name,
                                                     order.executed.price, order.executed.size))

        else:
            self.log('订单作废 %s, %s, isbuy=%i, size %i, open price %.2f' %
                     (order.data._name, order.getstatusname(), order.isbuy(), order.created.size,
                      order.data.open[0]))

        # 记录交易收益情况

    def notify_trade(self, trade):
        if trade.isclosed:
            self.log('毛收益 %0.2f, 扣佣后收益 % 0.2f, 佣金 %.2f, 市值 %.2f, 现金 %.2f' %
                     (
                         trade.pnl, trade.pnlcomm, trade.commission, self.broker.getvalue(),
                         self.broker.getcash()))

    def __init__(self, params=None):
        if params is not None:
            self.p.period = params['period']
        self.log("params : {}".format(params))

        # 上次交易股票的列表
        self.last_ranks = []
        # 从1号往后进入股票池
        self.stocks = self.datas[1:]
        # 记录以往订单，在再平衡日要全部取消未成交的订单
        self.orders = {}
        self.obv = {d: ObvIndex(data=d, period=self.p.period).value for d in self.stocks}

    def next(self):

        for stock in self.stocks:
            self.log("{} {} {}".format(stock._name, self.obv[stock][0], stock not in self.orders))
            if stock not in self.orders and self.obv[stock][0] > 0:
                size = int(abs((0.02 * self.broker.getvalue()) / stock.close[0]))
                self.orders[stock] = self.buy(data=stock, size=size, exectype=bt.Order.Close)

            elif stock in self.orders and self.obv[stock][0] < 0:
                self.close(data=stock)
                self.orders.pop(stock)
                print(self.orders[stock])
class BaseStrategy(bt.Strategy):

    def log(self, txt, dt=None, doprint=True):
        """ 日志函数，用于统一输出日志格式 """

        if doprint:
            dt = dt or self.datas[0].datetime.date(0)
            log.info('%s, %s' % (dt.isoformat(), txt))

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # 订单状态 submitted/accepted，无动作
            return

        # 订单完成
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('买单执行,%s, %.2f, %i' % (order.data._name,
                                                    order.executed.price, order.executed.size))

            elif order.issell():
                self.log('卖单执行, %s, %.2f, %i' % (order.data._name,
                                                     order.executed.price, order.executed.size))

        else:
            self.log('订单作废 %s, %s, isbuy=%i, size %i, open price %.2f' %
                     (order.data._name, order.getstatusname(), order.isbuy(), order.created.size, order.data.open[0]))

    # 记录交易收益情况
    def notify_trade(self, trade):
        if trade.isclosed:
            self.log('毛收益 %0.2f, 扣佣后收益 % 0.2f, 佣金 %.2f, 市值 %.2f, 现金 %.2f' %
                     (trade.pnl, trade.pnlcomm, trade.commission, self.broker.getvalue(), self.broker.getcash()))
