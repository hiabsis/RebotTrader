from strategy import *


class AroonStrategy(bt.Strategy):
    """
    Aroon 指标策略
    指标：https://school.stockcharts.com/doku.php?id=technical_indicators:aroon
    公式：
    Aroon-Up = ((25 - 自 25 天高点以来的天数)/25) x 100
    Aroon-Down = ((25 - 自 25 天低点以来的天数)/25) x 100
    策略一：
    买入 Aroon-Up >70  and Aroon-Down <30
    平仓 Aroon-Up <30  and Aroon-Down>70
    """
    params = dict(
        period=20,  # 周期
        high=80,
        low=20,
        is_log=False
    )

    def log(self, txt, dt=None):
        if self.p.is_log:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s,%s' % (dt.isoformat(), txt))

    def __init__(self):
        # 记录交易订单
        self.order = None
        # 阿隆指标
        self.aroon = bt.indicators.AroonUpDown(period=self.p.period, upperband=70, lowerband=30, plotname='aroon')

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
        if self.order:
            return
        # 如果订单为处理完成 继续处理
        if self.order:
            return
        # 没有持有仓位
        if not self.position:
            size = self.get_buy_unit()
            if self.aroon.aroonup[0] > self.p.low:
                self.buy(size=size)

        elif self.position.size > 0:
            if self.aroon.aroonup < self.p.high:
                self.close()

    def notify(self, order):
        if order.status in [order.Completed, order.Canceled, order.Margin]:
            if order.isbuy():
                self.log('执行买入, %.2f' % order.executed.price)
                self.order = None
            elif order.issell():
                self.log('执行卖出, %.2f' % order.executed.price)
                self.order = None


def create_aroon_strategy(params=None):
    c = create_cerebro()
    if params is None:
        c.addstrategy(AroonStrategy)
    else:
        c.addstrategy(AroonStrategy,
                      low=int(params['low']),
                      high=int(params['high']),
                      period=int(params["period"]))
    return c


if __name__ == '__main__':
    # file_name = "ETHUSDT_30m.csv"
    file_name = "ETHUSDT_1h.csv"
    path = setting.date_root_path + "\\" + file_name
    # 获取数据
    data = get_data(path)
    # 运行策略
    # run_strategy(create_aroon_strategy, data=data, is_show=True)
    # # 优化策略
    space = dict(
        period=hp.uniform('period', 1, 400),
        high=hp.uniform('high', 0, 100),
        low=hp.uniform('low', 0, 100),

    )
    op = Optimizer(data=data, space=space,
                   max_evals=1000,
                   create_strategy_func=create_aroon_strategy,
                   is_send_ding_task=True)
    params = op.run()
    op.run()
    # # 对策略进行可视化分析
    show_strategy(data, create_aroon_strategy, params=params, is_show=True)
    # 其他数据集的表现
    # batch_optimizer(create_aroon_strategy, space=space, is_send_ding_talk=True)
