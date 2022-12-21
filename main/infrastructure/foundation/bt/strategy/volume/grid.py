import numpy as np

from main.infrastructure.foundation.bt.actuator import *


class GridStrategy(bt.Strategy):

    def __init__(self, params=None):
        self.long_short = None
        self.highest = bt.indicators.Highest(self.data.high, period=100, subplot=False)
        self.lowest = bt.indicators.Lowest(self.data.low, period=100, subplot=False)
        mid = (self.highest + self.lowest) / 2
        perc_levels = [x for x in np.arange(
            1 + 0.005 * 5, 1 - 0.005 * 5 - 0.005 / 2, -0.005)]
        self.price_levels = [mid * x for x in perc_levels]
        self.last_price_index = None

    def next(self):
        if self.last_price_index is None:
            for i in range(len(self.price_levels)):
                if self.data.close > self.price_levels[i]:
                    self.last_price_index = i
                    self.order_target_percent(
                        target=i / (len(self.price_levels) - 1))
                    return
        else:
            signal = False
            while True:
                upper = None
                lower = None
                if self.last_price_index > 0:
                    upper = self.price_levels[self.last_price_index - 1]
                if self.last_price_index < len(self.price_levels) - 1:
                    lower = self.price_levels[self.last_price_index + 1]
                # 还不是最轻仓，继续涨，就再卖一档
                if upper is not None and self.data.close > upper:
                    self.last_price_index = self.last_price_index - 1
                    signal = True
                    continue
                # 还不是最重仓，继续跌，再买一档
                if lower is not None and self.data.close < lower:
                    self.last_price_index = self.last_price_index + 1
                    signal = True
                    continue
                break
            if signal:
                self.long_short = None
                self.order_target_percent(
                    target=self.last_price_index / (len(self.price_levels) - 1))


interval = "4h"
start = "2022-05-01 00:00:00"
end = "2022-12-20 00:00:00"
Actuator.run(GridStrategy, symbol="ETHUSDT", interval=interval, start_time=start, end_time=end)
