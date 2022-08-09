"""
日内交易,每天1%
"""
import datetime
import strategy
import backtrader
import dateutil
from util import data_util, date_util


class T0Strategy(backtrader.Strategy):

    def __init__(self):
        # 当日最低收盘价
        self.low_price = self.data.close[0]

    def is_next_day(self):
        return self.datas[0].datetime.date(0) != self.datas[0].datetime.date(-1)

    def get_buy_unit(self, position=0.1):
        """
        买入仓位
        :param position:
        :return:
        """

        size = self.broker.getcash() / self.data.high[0] * position
        if size == 0:
            size = 1
        return int(size)

    def is_close(self):
        """
        是否平仓
        :return:
        """
        pass

    def is_buy(self):
        """
        是否买入
        :return:
        """
        if self.low_price < self.data.close[0] < self.data.close[-1] < self.data.close[-2]:
            return True
        else:
            return False

    def update_today_lowest_price(self):
        """
        更新当日最低价格
        :return:
        """
        if self.low_price > self.data.close[0]:
            self.low_price = self.data.close[0]

    def next(self):
        # 第二天平仓
        if self.is_next_day():
            # 重新计算最低价格
            self.low_price = self.data.close[0]
            self.close()
            return
        # 更新当日最低价格
        self.update_today_lowest_price()
        # 是否买入
        if not self.is_buy():
            # 买入仓位
            size = self.get_buy_unit()
            self.buy(size=size)

    def start(self):

        print(self.position.size)
        print(self.position.price)


def create_t0_strategy(params):
    c = strategy.create_cerebro()
    if params is None:
        c.addstrategy(T0Strategy)
    else:
        c.addstrategy(T0Strategy, period=int(params['rend_period']))
    return c


if __name__ == '__main__':
    data = data_util.get_local_generic_csv_data('ETH', '1h')
    strategy.run_strategy(create_t0_strategy, data, is_show=True)
