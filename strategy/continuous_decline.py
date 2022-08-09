import datetime
import strategy
import backtrader as bt

from util import data_util


def create_continuous_decline_strategy(params=None):
    """
    设置策略参数
    :param c:
    :param params:
    :return:
    """
    c = strategy.create_cerebro()
    if params is None:
        c.addstrategy(ContinuousDeclineStrategy)
    else:
        c.addstrategy(ContinuousDeclineStrategy,
                      callback=params['callback'],
                      period=int(params['period']),
                      down_day=int(params['down_day']),
                      stop_loss=params['stop_loss'],
                      take_profit=params['take_profit'])
    return c


class ContinuousDeclineStrategy(bt.Cerebro):
    """
    阴跌策略
    """
    params = dict(
        callback=0.01,  # 价格回调比例
        period=133,
        down_day=6,
        stop_loss=133,  # 止损比例
        take_profit=0.15,  # 止盈比例
        limdays=3,
        limdays2=1000
    )

    def __init__(self):

        print(11)
        self.dataclose = self.datas[0].close
        self.sma = bt.ind.SMA(period=self.p.period, plot=False)
        self.order_list = list()
        super().__init__()

    def notify_order(self, order):
        if order.status == order.Completed:
            pass
        if not order.alive() and order.ref in self.orefs:
            self.order_list.remove(order.ref)

    def next(self):
        if self.order_list:  # order列表，用于存储尚未执行完成的订单
            return  # 有尚未执行的订单
        # 尚未进场
        if not self.position:
            # 获取近几日收盘价用于判断是否连续上涨
            last_closes = list()
            for i in range(self.p.down_day + 1):
                last_closes.append(self.dataclose[-i])

            # 连续N日下跌
            if last_closes == sorted(last_closes, reverse=True):
                orders = self.get_order()
                # 保存激活的的订单
                self.order_list = [o.ref for o in orders]

    def get_order(self):
        p1 = self.dataclose[0] * (1.0 - self.p.callback)
        p2 = p1 - self.p.stop_loss * p1
        p3 = p1 + self.p.take_profit * p1
        # 计算订单有效期
        validity_day = datetime.timedelta(self.p.validity_day)
        expired_day = valid3 = datetime.timedelta(self.p.expired_day)
        size = min(self.broker.getcash() / self.data.high[0], self.data.volume)
        orders = self.buy_bracket(size=size,
                                  price=p1, valid=validity_day,
                                  stopprice=p2, stopargs=dict(valid=expired_day),
                                  limitprice=p3, limitargs=dict(valid=valid3), )
        return orders


if __name__ == '__main__':
    data = data_util.get_local_generic_csv_data("ETH", "1h")
    strategy.run_strategy(create_continuous_decline_strategy, data, is_show=True)
