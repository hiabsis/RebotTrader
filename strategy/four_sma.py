import logging
import backtrader as bt
import datetime
from hyperopt import hp, fmin, tpe, Trials
from strategy import run_strategy
from util import to_json, load_csv_data, send_text_to_dingtalk


def add_four_sma_strategy(cerebro, params=None):
    if params is None:
        cerebro.addstrategy(FourSmaStrategy)
    else:
        cerebro.addstrategy(FourSmaStrategy,
                            sma1=int(params['sma1']),
                            sma2=int(params['sma2']),
                            sma3=int(params['sma3']),
                            sma4=int(params['sma4']),
                            limit_size=params['limit_size'],  # 仓位
                            stop_loss=params['stop_loss'],  # 止损比例
                            take_profit=params['take_profit'],  # 止盈比例
                            callback=params['callback']  # 价格回调
                            )
    return cerebro


class FourSmaStrategy(bt.Strategy):
    """
     四根移动曲线的策略
    """

    params = dict(
        sma1=20,
        sma2=50,
        sma3=100,
        sma4=200,
        limit_size=0.2,  # 仓位
        stop_loss=0.05,  # 止损比例
        take_profit=0.1,  # 止盈比例
        callback=0.01  # 价格回调
    )

    def __init__(self):
        self.sma1 = bt.ind.SMA(period=int(self.p.sma1))
        self.sma2 = bt.ind.SMA(period=int(self.p.sma2))
        self.sma3 = bt.ind.SMA(period=int(self.p.sma3))
        self.sma4 = bt.ind.SMA(period=int(self.p.sma4))
        self.order = None

    def get_buy_unit(self):
        size = min(int(self.broker.getcash() / self.data.high[0]) * self.p.limit_size, self.data.volume[0])
        if size == 0:
            size = 1
        return size

    def go_buy(self, price):
        p1 = price * (1.0 - self.p.callback)
        loss = p1 - self.p.stop_loss * price
        profit = p1 + self.p.take_profit * price
        valid1 = datetime.timedelta(5)
        valid2 = valid3 = datetime.timedelta(1000)
        size = self.get_buy_unit()
        print(size)
        os = self.buy_bracket(size=size,
                              price=p1, valid=valid1,
                              stopprice=loss, stopargs=dict(valid=valid2),
                              limitprice=profit, limitargs=dict(valid=valid3), )
        self.order = [o.ref for o in os]

    def next(self):
        print(self.sma1[0] > self.sma4[0])
        print(self.order)
        if self.order:
            return

        if not self.position:
            if self.sma1[0] > self.sma4[0]:
                self.go_buy(self.data.close[0])

        # else:
        #     if self.sma1[0] > self.sma2[0] > self.sma3[0] > self.sma4[0] \
        #             and self.colse[0] > self.sma2[0]:
        #         self.go_buy(self.sma2[0])
        #
        #     if self.sma1[0] > self.sma2[0] > self.sma3[0] > self.sma4[0] \
        #             and self.colse[0] > self.sma3[0]:
        #         self.go_buy(self.sma3[0])
        #     if self.sma1[0] > self.sma2[0] > self.sma3[0] > self.sma4[0] \
        #             and self.colse[0] > self.sma4[0]:
        #         self.go_buy(self.sma4[0])


class FourSmaStrategyOptimizer:

    def __init__(self, data, max_evals=500, is_send_ding_task=False):
        self.data = data
        self.max_evals = max_evals
        self.is_send_ding_task = is_send_ding_task
        self.params = None
        self.cash = 10000
        self.is_show = False

    # 参数空间
    space = dict(
        sma1=hp.uniform('sma1', 10, 400),
        sma2=hp.uniform('sma2', 10, 400),
        sma3=hp.uniform('sma3', 10, 400),
        sma4=hp.uniform('sma4', 10, 400),
        limit_size=hp.uniform('limit_size', 0.01, 1),
        stop_loss=hp.uniform('stop_loss', 0.02, 0.5),
        take_profit=hp.uniform('take_profit', 0.02, 1),
        callback=hp.uniform('callback', 0.02, 0.5),

    )

    def target_func(self, params):
        cerebro = run_strategy(func=add_four_sma_strategy, data=self.data,
                               cash=self.cash, params=params)
        return -cerebro.broker.getvalue()

    def run(self):
        trials = Trials()
        self.params = fmin(fn=self.target_func, space=self.space, algo=tpe.suggest, max_evals=500,
                           trials=trials)
        logging.info(self.params)
        return self.params

    def plot(self):
        self.is_show = True
        run_strategy(add_four_sma_strategy, self.params)
        self.is_show = False


def test_strategy():
    start = datetime.datetime.now().timestamp()
    path = "D:\\work\\git\\Tools\\static\\data\\DOTUSDT_1h.csv"
    data = load_csv_data(data_path=path)
    opt = FourSmaStrategyOptimizer(data=data)
    params = opt.run()
    cash = 100000
    cerebro = run_strategy(func=add_four_sma_strategy, data=data, params=params, cash=cash)
    end = datetime.datetime.now().timestamp()
    execute_time = (end - start) / 60

    info = {
        "策略名称": "FourSmaStrategy",
        "运行时间": f"{execute_time}分钟",
        "数据源": path,
        "收益率": f"{cerebro.broker.getvalue() / cash * 100} %",
        "参数": params
    }
    logging.info(info)
    send_text_to_dingtalk(to_json(info))


if __name__ == '__main__':
    # test_strategy()
    # p = {'callback': 0.21488525014793064, 'limit_size': 0.9708743568330783, 'sma1': 40.89721379712444,
    #      'sma2': 215.00863389625, 'sma3': 258.7324362160136, 'sma4': 187.1857942195504,
    #      'stop_loss': 0.47861893505409814, 'take_profit': 0.9267635997981061}
    path = "D:\\work\\git\\Tools\\static\\data\\DOTUSDT_1h.csv"
    data = load_csv_data(data_path=path)
    cerebro = run_strategy(func=add_four_sma_strategy, data=data, is_show=True)
