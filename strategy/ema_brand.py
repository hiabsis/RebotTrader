from strategy import *
from indicator import ema


class EmaBrandStrategy(bt.Strategy):
    params = dict(
        rend_period=20,
        top_ratio=1.1,
        low_ratio=0.9,
        is_log=False
    )

    def log(self, txt, dt=None):
        if self.p.is_log:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s,%s' % (dt.isoformat(), txt))

    def __init__(self):

        self.ema_brand = ema.EmaBandIndicator(rend_period=self.p.rend_period,
                                              top_ratio=self.p.top_ratio,
                                              low_ratio=self.p.low_ratio)
        self.order = None

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
        # # 如果订单为处理完成 继续处理
        if self.order:
            return
        size = self.get_buy_unit()
        # 没有持有仓位
        if not self.position:
            if self.data.open[0] > self.ema_brand.top[-1]:
                self.order = self.buy(size=size)  # 买入
        elif self.position.size > 0:
            # 在多头情况下，平仓条件
            if self.data.open[0] < self.ema_brand[-1]:
                # 最新价低于中线，多头清仓离场
                self.close()
                # self.order = self.sell(size=size)
        #
        # elif self.position.size < 0:
        #     # 在空头情况下，平仓条件
        #     if self.data.open[0] > self.top[-1]:
        #         # 最新价高于中线，空头清仓离场
        #         self.close()
        #         self.order = self.buy(size=size)
        pass

    def notify(self, order):
        if order.status in [order.Completed, order.Canceled, order.Margin]:
            if order.isbuy():
                self.log('执行买入, %.2f' % order.executed.price)
                self.order = None
            elif order.issell():
                self.log('执行卖出, %.2f' % order.executed.price)
                self.order = None


def create_ema_brand_strategy(params=None):
    c = create_cerebro()
    if params is None:
        c.addstrategy(EmaBrandStrategy)
    else:
        c.addstrategy(EmaBrandStrategy,
                      rend_period=int(params['rend_period']),

                      top_ratio=params['top_ratio'],
                      low_ratio=params['low_ratio']
                      )
    return c


"""
{
        "rend_period":2.484951624677545,
        "low_ratio":0.8258301256647608,
        "rend_period":127.46566571613769,
        "top_ratio":1.0545327011361696
}
    
"""
if __name__ == '__main__':
    data = data_util.get_local_generic_csv_data('ETHUSDT', '1h')
    # run_strategy(create_ema_brand_strategy, data, is_show=True)
    params = {
        "low_ratio": 0.46134730415159086,
        "rend_period": 3.294047310358513,
        "top_ratio": 1.0339538130692096
    }
    # run_strategy(create_strategy_func=create_ema_brand_strategy, data=data, params=params, is_show=True)
    space = dict(
        rend_period=hp.uniform('period', 1, 400),
        top_ratio=hp.uniform('h_period', 1, 2),
        low_ratio=hp.uniform('l_period', 0, 1),

    )
    opt = Optimizer(create_strategy_func=create_ema_brand_strategy, space=space, max_evals=1000, data=data,
                    name="EMA_通道策略",
                    is_send_ding_task=True)
    p = opt.run()

    # batch_optimizer(create_ema_brand_strategy, space, is_send_ding_talk=True, name="EmaBrandStrategy")
