"""
单移动线的对比
"""
import datetime

import strategy
import backtrader


class SingleStrategy(backtrader.Strategy):
    params = dict(
        period=30,
        stop_loss=0.05,  # 止损比例
        take_profit=0.1,  # 止盈比例
        validity_day=3,  # 订单有效期
        expired_day=1000,  # 订单失效期
    )

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


