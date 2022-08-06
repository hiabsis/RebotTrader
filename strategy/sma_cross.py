from strategy import *


class SmaCrossStrategy(bt.Strategy):
    params = dict(
        sma1=30,  # 需要优化的参数1，短期均线窗口
        sma2=200,  # 需要优化的参数2，长期均线窗口
        is_log=False  # 是否打印日志
    )

    def log(self, txt, dt=None):
        if self.p.is_log:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s,%s' % (dt.isoformat(), txt))

    def __init__(self):
        sma1 = bt.ind.SMA(period=int(self.params.sma1))  # 用int取整
        sma2 = bt.ind.SMA(period=int(self.params.sma2))  # 用int取整
        self.crossover = bt.ind.CrossOver(sma1, sma2)

        self.order = None

    def get_buy_unit(self):
        size = self.broker.getcash() / self.data.high[0] * 0.5
        if size == 0:
            size = 1
        return size

    def next(self):
        if self.order:
            return
        if not self.position:  # 不在场内，则可以买入
            if self.crossover[0] < 0:  # 死叉
                size = self.get_buy_unit()
                self.order = self.buy(size=size)  # 买入

        else:
            if self.crossover[0] > 0:  # 金叉
                self.close()  # 卖出

    def notify(self, order):
        if order.status in [order.Completed, order.Canceled, order.Margin]:
            if order.isbuy():
                self.log('执行买入, %.2f' % order.executed.price)
            elif order.issell():
                self.log('执行卖出, %.2f' % order.executed.price)

        self.order = None


def create_sma_cross_strategy(params=None):
    c = create_cerebro()
    if params is None:
        c.addstrategy(SmaCrossStrategy)
    else:
        c.addstrategy(SmaCrossStrategy,
                      sma1=int(params["sma1"]),
                      sma2=int(params["sma2"]))
    return c


if __name__ == '__main__':
    space = dict(
        sma1=hp.uniform("sma1", 10, 500),
        sma2=hp.uniform("sma2", 10, 500)
    )

    batch_optimizer(strategy_func=create_sma_cross_strategy,
                    name="均线交叉策略",
                    space=space,
                    is_send_ding_talk=True)
    path = "/static/data/BNBUSDT_1h.csv"
    # data = get_data(path)
    # params = {
    #     'sma1': "350",
    #     'sma2': '390'
    # }
    # run_strategy(create_strategy_func=create_sma_cross_strategy, data=data, params=params, is_show=True)
    # path = show_strategy_analyze(data,
    #                              create_strategy_func=create_sma_cross_strategy,
    #                              params=params,
    #                              is_show=True)
    #
    # print(path)
    # path = show_strategy_pyfolio(data,
    #                              create_strategy_func=create_sma_cross_strategy,
    #                              params=params,
    #                              is_show=True)
    # print(path)
