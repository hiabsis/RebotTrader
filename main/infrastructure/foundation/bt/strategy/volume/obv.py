import backtrader as bt
from hyperopt import hp

from main.infrastructure.foundation.bt.optimizer import MuOptimizer
from main.infrastructure.foundation.logging import log


class StampDutyCommissionScheme(bt.CommInfoBase):
    """
    本佣金模式下，买入股票仅支付佣金，卖出股票支付佣金和印花税.
    """
    params = (
        ('stamp_duty', 0.005),  # 印花税率
        ('commission', 0.001),  # 佣金率
        ('stocklike', True),
        ('commtype', bt.CommInfoBase.COMM_PERC),
    )

    def _getcommission(self, size, price, pseudoexec):
        """
        If size is greater than 0, this indicates a long / buying of shares.
        If size is less than 0, it idicates a short / selling of shares.
        """

        if size > 0:  # 买入，不考虑印花税
            return size * price * self.p.commission
        elif size < 0:  # 卖出，考虑印花税
            return - size * price * (self.p.stamp_duty + self.p.commission)
        else:
            return 0  # just in case for some reason the size is 0.


class SMAStrategy(bt.Strategy):
    params = dict(
        rebal_monthday=[1],  # 每月1日执行再平衡
        num_volume=20,  # 成交量取前100名
        period=5,
        buy_point=0.9,
        sell_point=1.1
    )

    # 日志函数
    def log(self, txt, dt=None, doprint=False):
        """ 日志函数，用于统一输出日志格式 """

        if doprint:
            dt = dt or self.datas[0].datetime.date(0)
            log.info('%s, %s' % (dt.isoformat(), txt))

    def __init__(self, params=None):
        if params is not None:
            self.p.buy_point = params["buy_point"]
            self.p.sell_point = params["sell_point"]
            self.log("参数 : {}".format(params), True)
        self.ranks = None
        self.currDate = None
        self.lastRanks = []  # 上次交易股票的列表
        # 0号是指数，不进入选股池，从1号往后进入股票池
        self.stocks = self.datas[1:]

        # 记录以往订单，在再平衡日要全部取消未成交的订单
        self.order_list = []

        # 移动平均线指标
        self.sma = {d: bt.ind.SMA(d, period=self.p.period) for d in self.stocks}
        # obv
        # self.obv = {d: bt.talib.OBV(self.stocks.close, self.stocks.volume) for d in self.stocks}
        # 定时器
        self.add_timer(
            when=bt.Timer.SESSION_START,
            monthdays=self.p.rebal_monthday,  # 每月1号触发再平衡
            monthcarry=True,  # 若再平衡日不是交易日，则顺延触发notify_timer
        )

    def notify_timer(self, timer, when, *args, **kwargs):
        # 只在5，9，11月的1号执行再平衡
        if self.data0.datetime.date(0).month in [1, 2, 3, 4, 5, 6, 7, 8, 10, 11]:
            self.rebalance_portfolio()  # 执行再平衡

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

    def rebalance_portfolio(self):
        # 从指数取得当前日期
        self.currDate = self.data0.datetime.date(0)
        self.log('执行再平衡 当前日期 {} {}'.format(self.currDate, len(self.stocks)))
        if len(self.datas[0]) == self.data0.buflen():
            return
        # 取消以往所下订单（已成交的不会起作用）
        for order in self.order_list:
            self.cancel(order)
        # 按成交量从大到小排序
        self.ranks = [d for d in self.stocks if d.close[0] > 1 and d.close[0] > self.sma[d][0]]
        self.ranks.sort(key=lambda d: d.volume, reverse=True)  # 按成交量从大到小排序
        # 取前num_volume名
        self.ranks = self.ranks[0:self.p.num_volume]
        # 无股票选中，则返回
        if len(self.ranks) == 0:
            return
        #  以往买入的标的，本次不在标的中，则先平仓
        data_toclose = set(self.lastRanks) - set(self.ranks)
        for d in data_toclose:
            self.log('sell 平仓 {} 仓位 {}'.format(d._name, self.getposition(d).size))
            o = self.close(data=d)
            # 记录订单
            self.order_list.append(o)
        buypercentage = (1 - 0.02) / len(self.ranks)
        targetvalue = buypercentage * self.broker.getvalue()
        self.ranks.sort(key=lambda d: self.broker.getvalue([d]), reverse=True)
        self.log('下单, 标的个数 %i, targetvalue %.2f, 当前总市值 %.2f' %
                 (len(self.ranks), targetvalue, self.broker.getvalue()))

        for d in self.ranks:
            size = int(
                abs((self.broker.getvalue([d]) - targetvalue) / d.open[1]))

            if self.broker.getvalue([d]) > targetvalue:  # 持仓过多，要卖
                # 次日跌停价近似值
                lowerprice = d.close[0] * self.p.sell_point

                o = self.sell(data=d, size=size, exectype=bt.Order.Limit,
                              price=lowerprice)
            else:  # 持仓过少，要买
                # 次日涨停价近似值
                upperprice = d.close[0] * self.p.buy_point
                o = self.buy(data=d, size=size, exectype=bt.Order.Limit,
                             price=upperprice)
            self.order_list.append(o)  # 记录订单
        self.lastRanks = self.ranks  # 跟踪上次买入的标的


space = dict(
    buy_point=hp.uniform("buy_point", 0.5, 4),
    sell_point=hp.uniform("sell_point", 0.5, 2)
)

interval = "1d"
start = "2020-12-20 00:00:00"
end = "2022-12-20 00:00:00"
params = dict(
    rebal_monthday=[1],  # 每月1日执行再平衡
    num_volume=20,  # 成交量取前100名
    period=5,
    buy_point=0.9,
    sell_point=1.1
)
# MuActuator.run(SMAStrategy, '1d', start_time=start, end_time=end, plot=False, params=params)

optimizer = MuOptimizer()
optimizer.set_space(space)
optimizer.set_strategy(SMAStrategy)
optimizer.set_date(interval=interval, start=start, end=end)
optimizer.run(evals=100)
