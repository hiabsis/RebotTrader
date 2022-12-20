import backtrader
from hyperopt import hp

import actuator
import util


class SmaStrategy(backtrader.Strategy):
    params = dict(
        stop_loss=0.05,
        take_profit=0.1,
        position=0.5,
        validity_day=3,
        expired_day=1000,
        fast=50,
        slow=200
    )



    def __init__(self, params=None):
        self.handle_params(params)
        self.fast = backtrader.ind.SMA(period=self.p.fast)
        self.slow = backtrader.ind.SMA(period=self.p.slow)

    def handle_params(self, params=None):
        if params is None:
            return
        if 'fast' in params:
            self.p.fast = params['fast']
        if 'slow' in params:
            self.p.slow = params['slow']

    def next(self):
        if not self.position:
            if self.slow[-1] < self.fast[-1] and \
                    self.data.close[0] > self.slow[-1]:
                size = min(int(self.broker.getcash() / self.data.high[0] * self.p.position), self.data.volume)
                self.buy(size=size)
        if self.position:
            if self.slow[-1] < self.fast[-1] and \
                    self.data.close[0] < self.fast[0]:
                self.close()


if __name__ == '__main__':
    data = util.get_local_generic_csv_data('ETH', '1h')
    # actuator.Actuator(data, SmaStrategy).run()
    space = dict(
        fast=hp.randint('fast', 500),
        slow=hp.randint('slow', 1000),

    )
    actuator.Actuator(data, SmaStrategy).opt(space, 2000)
