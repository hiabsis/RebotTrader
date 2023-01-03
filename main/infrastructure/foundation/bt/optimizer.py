from hyperopt import Trials, fmin, tpe

from main.infrastructure.foundation.bt.actuator import Actuator, MuActuator
from main.infrastructure.foundation.logging import log
from main.infrastructure.rpc.binance.client import BinanceClint
from main.infrastructure.utils.bt import BackTradeUtil


class Optimizer:

    def __init__(self):
        self.data = None
        self.space = None
        self.strategy = None
        self.asset = 0
        self.params = None

    def set_date(self, symbol, interval, start_time=None, end_time=None):
        BinanceClint.download_kline(symbol, interval)
        self.data = BackTradeUtil.load_csv(symbol, interval, start=start_time, end=end_time)

    def set_strategy(self, strategy):
        self.strategy = strategy

    def set_space(self, space):
        self.space = space

    def target_func(self, params):
        log.info("调优参数 ：{}".format(params))
        cerebro = Actuator.run(data=self.data, params=params, strategy=self.strategy, plot=False)
        if self.asset < cerebro.broker.getvalue():
            self.asset = cerebro.broker.getvalue()
        return -cerebro.broker.getvalue()

    def run(self, evals=10000):
        trials = Trials()
        self.params = fmin(fn=self.target_func, space=self.space, algo=tpe.suggest, max_evals=evals,
                           trials=trials)
        log.info(f'最优参数: {self.params}')

        return self.params

def notify_op():
    pass

class MuOptimizer:

    def __init__(self):
        self.end = None
        self.start = None
        self.interval = None
        self.space = None
        self.strategy = None
        self.asset = 0
        self.params = None

    def set_strategy(self, strategy):
        self.strategy = strategy

    def set_space(self, space):
        self.space = space

    def set_date(self, interval, start, end):
        self.interval = interval
        self.start = start
        self.end = end

    def target_func(self, params):
        cerebro = MuActuator.run(self.strategy, self.interval, start_time=self.start, end_time=self.end,
                                 plot=False, params=params)
        if self.asset < cerebro.broker.getvalue():
            self.asset = cerebro.broker.getvalue()
        return -cerebro.broker.getvalue()

    def run(self, evals=1000):
        trials = Trials()
        self.params = fmin(fn=self.target_func, space=self.space, algo=tpe.suggest, max_evals=evals,
                           trials=trials)
        log.info(f'最优参数: {self.params}')
        return self.params
