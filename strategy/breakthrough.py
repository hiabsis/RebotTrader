from strategy import *


class BreakthroughStrategy(Strategy):
    """
    """
    params = dict(
        break_through=0.04,  # 上涨幅度
        callback=0.02,  # 价格回调比例
        period=100,  # sma周期
        down_day=5,  # 连续下跌天数
        stop_loss=0.05,  # 止损比例
        take_profit=0.1,  # 止盈比例
        validity_day=3,  # 订单有效期
        expired_day=1000,  # 订单失效期
    )

    def notify_order(self, order):
        if order.status == order.Completed:
            self.holdstart = len(self)
        if not order.alive() and order.ref in self.orefs:
            self.order.remove(order.ref)

    def __init__(self):
        self.holdstart = None
        self.dataclose = self.datas[0].close  # 收盘价
        self.sma = bt.ind.SMA(period=self.p.period, plot=True)  # SMA
        self.order = list()  # order列表，用于存储尚未执行完成的订单

    def buy_loss_order(self):
        p1 = self.dataclose[0] * (1.0 - self.p.callback)
        p2 = p1 - self.p.stop_loss * p1
        p3 = p1 + self.p.take_profit * p1
        # 计算订单有效期
        validity_day = datetime.timedelta(self.p.validity_day)
        expired_day = valid3 = datetime.timedelta(self.p.expired_day)
        size = min(self.broker.getcash() / self.data.high[0], self.data.volume)
        od = self.buy_bracket(size=size,
                              price=p1, valid=validity_day,
                              stopprice=p2, stopargs=dict(valid=expired_day),
                              limitprice=p3, limitargs=dict(valid=valid3), )
        self.order = [o.ref for o in od]

    def next(self):
        # 有尚未执行的订单
        if self.orefs:
            return
            # 尚未进场
            # 获取近几日收盘价用于判断是否连续下跌
        last_closes = list()
        for i in range(1, self.p.down_day + 1):
            last_closes.append(self.dataclose[-i])
        if not self.position:

            # 判断十分突破
            is_break = False
            if self.dataclose[0] > self.dataclose[-1] \
                    and (self.data.high[0] - self.dataclose[0]) / self.dataclose[0] > self.p.break_through:
                is_break = True
            # 连续N日下跌 在 sma上方
            if last_closes == sorted(last_closes, reverse=False) and is_break and self.dataclose[0] > self.sma[0]:
                self.buy_loss_order()





def add_breakthrough_strategy(c: Cerebro, params=None):
    """
    设置策略参数
    :param c:
    :param params:
    :return:
    """
    if params is None:
        return c.addstrategy(BreakthroughStrategy)
    c.addstrategy(BreakthroughStrategy,
                  break_through=params['break_through'],
                  callback=params['callback'],
                  period=int(params['period']),
                  down_day=int(params['down_day']),
                  stop_loss=params['stop_loss'],
                  take_profit=params['take_profit'])
    return c
