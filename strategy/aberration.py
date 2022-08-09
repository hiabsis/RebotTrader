from strategy import *


class AberrationStrategy(bt.Strategy):
    params = dict(
        period=30,  # 周期
        is_log=False
    )

    def log(self, txt, dt=None):
        if self.p.is_log:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s,%s' % (dt.isoformat(), txt))

    def __init__(self):
        # 记录交易订单
        self.order = None
        # boll上轨
        self.top = bt.indicators.BollingerBands(period=self.p.period).top
        # boll下轨
        self.bot = bt.indicators.BollingerBands(period=self.p.period).bot
        # boll中轨
        self.mid = bt.indicators.BollingerBands(period=self.p.period).mid

        # 当前价格
        self.price = self.data.open

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
        # 如果订单为处理完成 继续处理
        if self.order:
            return
        # 没有持有仓位
        if not self.position:
            size = self.get_buy_unit()
            # K线下穿下轨,开空仓
            if self.price[0] > self.top[0]:
                self.order = self.buy(size=size)  # 买入
            # K线下穿下轨,开空仓
            if self.price[0] < self.bot[0]:
                self.order = self.sell(size=size)

        elif self.position.size > 0:
            # 在多头情况下，平仓条件
            if self.price[0] < self.bot[0]:
                # 最新价低于中线，多头清仓离场
                self.close()
        elif self.position.size < 0:
            # 在空头情况下，平仓条件
            if self.price[0] > self.top[0]:
                # 最新价高于中线，空头清仓离场
                self.close()

    def notify(self, order):
        if order.status in [order.Completed, order.Canceled, order.Margin]:
            if order.isbuy():
                self.log('执行买入, %.2f' % order.executed.price)
                self.order = None
            elif order.issell():
                self.log('执行卖出, %.2f' % order.executed.price)
                self.order = None


def create_aberration_strategy(params=None):
    c = create_cerebro()
    if params is None:
        c.addstrategy(AberrationStrategy)
    else:
        c.addstrategy(AberrationStrategy,
                      period=int(params["period"]))
    return c


if __name__ == '__main__':
    file_name = "ETHUSDT_30m.csv"
    path = setting.date_root_path + "\\" + file_name
    # 获取数据
    data = get_data(path)
    # 优化策略
    space = dict(
        period=hp.uniform('period', 10, 500)
    )
    op = Optimizer(data=data, space=space, create_strategy_func=create_aberration_strategy)
    params = op.run()
    params = {
        "period": 10
    }
    # # 对策略进行可视化分析
    analyze_strategy(data, create_aberration_strategy, params=params, is_show=True)
    # # 其他数据集的表现
    # batch_optimizer(create_aberration_strategy, space=space, is_send_ding_talk=True)
