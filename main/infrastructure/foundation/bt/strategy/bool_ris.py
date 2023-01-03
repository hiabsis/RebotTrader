import backtrader as bt

from main.infrastructure.foundation.logging import log
from main.resource.config import ENABLE_STRATEGY_LOG


class BollRsiStrategy(bt.Strategy):
    def __init__(self, params: dict = None):
        self.order_list = None
        if params is None:
            self.log("params : {}".format(params))
            self.p.rsi_period = params['rsi_period']
            self.p.bool_period = params['bool_period']

        # 0号是指数，不进入选股池，从1号往后进入股票池
        self.stocks = self.datas[1:]
        # 记录以往订单，在再平衡日要全部取消未成交的订单
        self.order_list = []
        self.sma = {d: bt.ind.SMA(d, period=self.p.sma_perios) for d in self.stocks}
        self.top = {d: bt.ind.BollingerBands(d, period=self.p.bool_period).top for d in self.stocks}
        self.bot = {d: bt.ind.BollingerBands(d, period=self.p.bool_period).bot for d in self.stocks}
        self.rsi = {d: bt.ind.RSI(period=self.p.rsi_period) for d in self.stocks}
        # 最大有效期
        self.max_period = max(max(self.p.bool_period, self.p.rsi_period), self.p.sma_perios)
        self.ranks = []
        self.last_ranks = []

    def log(self, txt, dt=None):
        """ 日志函数，用于统一输出日志格式 """

        if ENABLE_STRATEGY_LOG:
            dt = dt or self.datas[0].datetime.date(0)
            log.info('%s, %s' % (dt.isoformat(), txt))

    params = dict(
        rsi_period=30,
        bool_period=30,
        sma_perios=200,
        num_volume=20,
    )

    def make_trade(self):
        self.log("交易 开始")
        # 取消以往所下订单（已成交的不会起作用）
        for o in self.order_list:
            self.cancel(o)
        self.order_list = []  # 重置订单列表

        self.ranks = [d for d in self.stocks if
                      d.marketdays > self.max_period
                      # 收盘价大于 1
                      and d.close[-1] > 1
                      # ris 小于30
                      and d.rsi[d][-1] < 30
                      # 碰到底部
                      and d.bot[d][-1] > d.close[-1]
                      ]
        self.ranks.sort(key=lambda d: d.volume, reverse=True)  # 按成交量从大到小排序
        self.ranks = self.ranks[0:self.p.num_volume]  # 取前num_volume名

        if len(self.ranks) == 0:  # 无股票选中，则返回
            return
        # 3 以往买入的标的，本次不在标的中，则先平仓
        data_toclose = set(self.last_ranks) - set(self.ranks)
        for d in data_toclose:
            print('sell 平仓', d._name, self.getposition(d).size)
            o = self.close(data=d)
            self.order_list.append(o)  # 记录订单
        buypercentage = (1 - 0.02) / len(self.ranks)

        # 得到目标市值
        targetvalue = buypercentage * self.broker.getvalue()
        # 为保证先卖后买，股票要按持仓市值从大到小排序
        self.ranks.sort(key=lambda d: self.broker.getvalue([d]), reverse=True)
        self.log('下单, 标的个数 %i, targetvalue %.2f, 当前总市值 %.2f' %
                 (len(self.ranks), targetvalue, self.broker.getvalue()))
        for d in self.ranks:
            # 按次日开盘价计算下单量，下单量是100的整数倍
            size = 100
            validday = d.datetime.datetime(1)  # 该股下一实际交易日
            if self.broker.getvalue([d]) > targetvalue:  # 持仓过多，要卖
                lowerprice = d.close[0] * 1.1 + 0.02
                o = self.sell(data=d, size=size, exectype=bt.Order.Limit,
                              price=lowerprice, valid=validday)
            else:  # 持仓过少，要买
                upperprice = d.close[0] * 0.9 - 0.02
                o = self.buy(data=d, size=size, exectype=bt.Order.Limit,
                             price=upperprice, valid=validday)

            self.order_list.append(o)  # 记录订单

        self.last_ranks = self.ranks  # 跟踪上次买入的标的
        self.log("交易 结束")
