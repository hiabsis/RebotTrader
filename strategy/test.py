from strategy import *


def main(data, strategy, pf=True):
    cerebro = bt.Cerebro()
    cerebro.adddata(data)
    # 加载策略
    cerebro.addstrategy(strategy)
    # 设置初始资本为10,000
    startcash = 100000
    cerebro.broker.setcash(startcash)
    # 设置交易手续费为 0.1%
    cerebro.broker.setcommission(commission=0.001)
    cerebro.run()
    # 获取回测结束后的总资金
    portvalue = cerebro.broker.getvalue()
    pnl = portvalue - startcash
    if pf:
        print(f'总资金: {round(portvalue, 2)}')
        print(f'净收益: {round(pnl, 2)}')
    cerebro.plot()


# class EmaChainIndicator(bt.Indicator):
#     lines = ('mid', 'top', 'bot',)
#     params = (('ema_period', 20),
#               ('rend_period', 20),
#               ('h_period', 10),
#               ('l_period', 10),)
#     # 与价格在同一张图
#     plotinfo = dict(subplot=False)
#     def __init__(self):
#         ema = bt.ind.EMA(self.data, period=self.p.ema_period)
#         self.mid = bt.ind.EMA(ema, period=self.p.ema_period)
#         self.top = bt.ind.EMA(ema, period=self.p.ema_period)
#         self.bot = bt.ind.EMA(ema, period=self.p.ema_period)
#         super(EmaChainIndicator, self).__init__()


class EmaBand(bt.Indicator):
    lines = ('mid', 'top', 'bot',)
    params = (('ema_period', 20),
              ('rend_period', 3),
              ('top_ratio', 1.1),
              ('low_ratio', 0.9),)
    # 与价格在同一张图
    plotinfo = dict(subplot=False)

    def __init__(self):
        ema = bt.ind.EMA(self.data, period=self.p.ema_period)
        h_ema = bt.ind.EMA(self.data.high, period=self.p.ema_period)
        l_ema = bt.ind.EMA(self.data.low, period=self.p.ema_period)
        # ha = bt.indicators.Average(self.data.high, period=self.p.h_period)
        # la = bt.indicators.Average(self.data.low, period=self.p.l_period)
        # 计算上中下轨线
        self.l.mid = bt.ind.EMA(ema, period=self.p.ema_period)
        # ha = bt.indicators.Average(l_ema, period=self.p.rend_period)
        # la = bt.indicators.Average(self.data.low, period=self.p.rend_period)
        self.l.top = bt.ind.EMA(self.mid * self.p.top_ratio,
                                period=self.p.ema_period)
        self.l.bot = bt.ind.EMA(self.mid * self.p.low_ratio,
                                period=self.p.ema_period)
        super(EmaBand, self).__init__()


def create():
    c = create_cerebro()
    c.addstrategy(EmaBand)
    return c


if __name__ == '__main__':
    data = data_util.get_local_generic_csv_data("BTCUSDT", "1h")
    main(data, EmaBand)
