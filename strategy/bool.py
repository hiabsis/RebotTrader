from scipy.constants import hp

from strategy import *

gloVar = dict(
    buy_count=0,
    sell_count=0
)


def create_boll_strategy(p):
    c = create_cerebro()
    if p is None:
        c.addstrategy(BollStrategy)
    else:
        c.addstrategy(BollStrategy, period=int(p["period"]))

    return c


class BollStrategy(bt.Strategy):
    params = dict(
        is_log=False,
        period=20
    )

    def log(self, txt, dt=None):
        if self.p.is_log:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s,%s' % (dt.isoformat(), txt))

    def __init__(self):
        # 指定价格序列
        self.dataclose = self.datas[0].close
        # 交易订单状态初始化
        self.order = None
        self.lines.top = bt.indicators.BollingerBands(period=self.p.period).top
        self.lines.bot = bt.indicators.BollingerBands(period=self.p.period).bot

    def get_buy_unit(self):
        size = self.broker.getcash() / self.data.high[0] * 0.5
        if size == 0:
            size = 1
        return size

    def next(self):
        # 检查订单状态
        if self.order:
            return

        # 检查持仓
        if not self.position:
            # 没有持仓，买入开仓
            if self.dataclose <= self.lines.bot[0]:
                self.order = self.buy(size=self.get_buy_unit())


        else:
            # 手里有持仓，判断卖平
            if self.dataclose >= self.lines.top[0]:
                self.close()

    def notify(self, order):

        if order.status in [order.Submitted, order.Accepted]:
            if order.status in [order.Submitted]:
                self.log("提交订单......")
            if order.status in [order.Accepted]:
                self.log("接受订单......")
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enougth cash
        if order.status in [order.Completed, order.Canceled, order.Margin]:
            if order.isbuy():
                self.log('执行买入, %.2f' % order.executed.price)
                gloVar['buy_count'] = gloVar['buy_count'] + 1
            elif order.issell():
                self.log('执行卖出, %.2f' % order.executed.price)
                gloVar['sell_count'] = gloVar['sell_count'] + 1
            self.bar_executed = len(self)

        self.log("订单完成......")

        # Write down: no pending order
        self.order = None


if __name__ == '__main__':
    space = dict(
        period=hp.uniform("period", 20, 500)
    )
    path = "/static/data/BNBUSDT_1h.csv"
    show_strategy_analyze(data=get_data(path), create_strategy_func=create_boll_strategy,
                          is_show=True)
