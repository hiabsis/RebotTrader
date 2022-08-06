from base import *


class ContinuousDeclineFuturesStrategy(Strategy):
    """
    阴跌期货版本策略
    """
    params = dict(
        callback=0.01,  # 价格回调比例
        period=133,
        down_day=6,
        stop_loss=133,  # 止损比例
        take_profit=0.15,  # 止盈比例
        limdays=3,
        limdays2=1000,
        hold=10,
    )

    def __init__(self):
        self.holdstart = None
        self.dataclose = self.datas[0].close
        self.sma = bt.ind.SMA(period=self.p.period, plot=False)
        self.order_list = list()

    def next(self):
        if self.order_list:  # order列表，用于存储尚未执行完成的订单
            return  # 有尚未执行的订单
        # 尚未进场
        if not self.position:
            # 获取近几日收盘价用于判断是否连续上涨
            last_closes = list()
            for i in range(self.p.down_day + 1):
                last_closes.append(self.dataclose[-i])
            # 判断趋势
            trend = self.dataclose[0] > self.sma[0]
            size = min(self.broker.getcash() / self.sma[0], self.data.volume[0])
            size = int(size)
            if size == 0:
                size = 1
            # 连续N日下跌
            if False and last_closes == sorted(last_closes, reverse=True) and trend:
                print("buy")
                close = self.dataclose[0]
                p1 = close * (1.0 - self.p.callback)
                p2 = p1 - self.p.stop_loss * close
                p3 = p1 + self.p.take_profit * close
                # 计算订单有效期
                valid1 = datetime.timedelta(self.p.limdays)
                valid2 = valid3 = datetime.timedelta(self.p.limdays2)
                os = self.buy_bracket(size=size,
                                      price=p1,
                                      valid=valid1,
                                      stopprice=p2,
                                      stopargs=dict(valid=valid2),
                                      limitprice=p3,
                                      limitargs=dict(valid=valid3), )
                # 保存激活的的订单
                self.orefs = [o.ref for o in os]

            # 连续N日下跌
            if last_closes == sorted(last_closes, reverse=False) and not trend:
                print("sell")
                close = self.dataclose[0]
                p1 = close * (1.0 - self.p.callback)
                p2 = p1 + self.p.stop_loss * close
                p3 = p1 - self.p.take_profit * close
                # 计算订单有效期
                valid1 = datetime.timedelta(self.p.limdays)
                valid2 = valid3 = datetime.timedelta(self.p.limdays2)
                os = self.sell_bracket(size=size,
                                       price=p1,
                                       valid=valid1,
                                       stopprice=p2,
                                       stopargs=dict(valid=valid2),
                                       limitprice=p3,
                                       limitargs=dict(valid=valid3), )
                # 保存激活的的订单
                self.orefs = [o.ref for o in os]


def test_continuous_decline_futures_strategy():
    path = "/static/data/ETHUSDT_1h.csv"
    data = load_csv_data(path)
    cerebro = create_cerebro()
    cerebro.adddata(data)
    cerebro.addstrategy(ContinuousDeclineFuturesStrategy)
    cerebro.broker.setcommission(
        commission=0.01,
        stocklike=True
    )
    cerebro.run()
    cerebro.plot()
