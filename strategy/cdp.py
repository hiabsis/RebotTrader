"""
中值CDP = (前一日最高价+ 前一日最低价+ 2×前一日收盘价)/4btw，
CDP也存在着另一种计算方式，会考虑到开盘价
最高值AH = CDP + (前一日最高价 － 前一日最低价)
近高值NH= 2×CDP － 前一日最低价
近低值NL = 2×CDP－ 前一日最高价
最低值AL = CDP － (前一日最高价 － 前一日最低价)

计算出AH、NH、CDP、NL、AL这5个数值之后，一般常用的交易原则就是，判断今日开盘价在CDP这5个数值的哪一个位置上。
在行情波动并不大的时候，开盘价一般在近高值NH和近低值NL之间，可以在近低值NL附近看多/买入，在近高值NH附近看空/卖出。
在行情波动东较大的时候，开盘价可能跳空高开在最高值AH之上，或者跳空低开在最低值AL之下，一般意味着可能要“搞事情”，有大行情发生。
于是呢，交易者可以开启“追涨杀跌”模式，在最高值AH附近看多/买入，在最低值AL附件看空/卖出。

"""
import dateutil
from hyperopt import hp

import strategy
import backtrader

from util import data_util


class CDPStrategy(backtrader.Strategy):
    params = dict(
        period=24,
        bwt=4,

        buy_line='ah',

        close_line='nl',
    )

    def is_buy(self):
        if self.p.buy_line == 'ah':
            return self.data.close[0] > self.ah[-1]
        if self.p.buy_line == 'nh':
            return self.data.close[0] > self.nh[-1]
        if self.p.buy_line == 'nl':
            return self.data.close[0] > self.nl[-1]
        if self.p.buy_line == 'al':
            return self.data.close[0] > self.al[-1]

        return self.data.close[0] > self.ah[-1]

    def is_close(self):
        if self.p.buy_line == 'ah':
            return self.data.close[0] < self.ah[-1]
        if self.p.buy_line == 'nh':
            return self.data.close[0] < self.nh[-1]
        if self.p.buy_line == 'nl':
            return self.data.close[0] < self.nl[-1]
        if self.p.buy_line == 'al':
            return self.data.close[0] < self.al[-1]

        return self.data.close[0] < self.nl[-1]

    def init_params(self, params):
        if params is None:
            return
        if "period" in params:
            self.p.period = params['period']
        if "bwt" in params:
            self.p.bwt = params['bwt']
        if "buy_line" in params:
            self.p.buy_line = params['buy_line']
        if "close_line" in params:
            self.p.close_line = params['close_line']

    def __init__(self, params=None):
        self.init_params(params)
        # 前一日最高价
        ph = backtrader.indicators.Highest(self.data.high, period=self.p.period)
        # 前一日最低价
        pl = backtrader.indicators.Lowest(self.data.low, period=self.p.period)
        # 前一日收盘价
        pc = backtrader.indicators.Lowest(self.data.close, period=self.p.period)
        self.cdp = (ph + pl + 2 * pc) / self.p.bwt
        self.ah = self.cdp + (ph - pl)
        self.nh = 2 * self.cdp - pl
        self.nl = 2 * self.cdp - ph
        self.al = self.cdp - (ph - pl)

        self.order = None

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

    def next(self):
        if self.order:
            return

        if not self.position:
            size = self.get_buy_unit()
            if self.data.open[0] > self.ah[-1]:
                self.order = self.buy(size=size)

        if self.position.size > 0:
            if self.data.close < self.nl[-1]:
                self.close()

    def notify(self, order):
        self.order = None


def create_cdp_strategy(params):
    c = strategy.create_cerebro()
    if params:
        c.addstrategy(CDPStrategy, params=params)
    else:
        c.addstrategy(CDPStrategy)
    return c


if __name__ == '__main__':
    data = data_util.get_local_generic_csv_data('BNB', '1h')

    space = dict(
        buy_line=hp.choice('buy_line', ['al', 'ah', 'nl', 'nh']),
        close_line=hp.choice('close_line', ['al', 'ah', 'nl', 'nh']),
        period=hp.randint('period', 24 * 3),
        bwt=hp.randint('bwt', 6)
    )
    opt = strategy.Optimizer(data, space, create_cdp_strategy, max_evals=500, is_send_ding_task=True)
    opt.run()
    strategy.batch_optimizer(create_cdp_strategy, space,
                             max_evals=1000,
                             strategy_name="CDP策略",
                             is_send_ding_talk=True)
    params = {'bwt': 4, 'period': 30}
    strategy.run_strategy(create_strategy_func=create_cdp_strategy, params=params, data=data, is_show=True)
    strategy.simple_analyze(func=create_cdp_strategy, data=data)
