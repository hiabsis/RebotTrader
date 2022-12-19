"""
交易量突破策略
"""

import backtrader as bt

from main.infrastructure.foundation.bt.actuator import Actuator
from main.infrastructure.foundation.logging import log


class VolumeBreakthroughIndex(bt.Indicator):
    lines = (
        'value',
    )
    params = (
        # 放量值
        ('break_volume', 5),
        ('break_ema', 5),

    )  #

    # plotinfo = dict(
    #     plot=True,
    #     subplot=False,  # 与价格在同一张图
    #     plotname='交易量突破',
    # )

    def next(self):
        volume = 0
        for i in range(self.p.break_ema):
            volume += self.data.volume[-i - 2]
        volume = (volume / self.p.break_ema) * self.p.break_volume
        if self.data.volume[0] > volume:
            self.l.value[0] = 1
        else:
            self.l.value[0] = 0
        if self.data.close[0] < self.data.open[0]:
            self.l.value[0] = -1 * self.l.value[0]


class VolumeBreakthroughStrategy(bt.Strategy):
    def __init__(self):
        self.is_break = VolumeBreakthroughIndex().value

    def next(self):
        log.info(" {} {}".format(self.data.volume[0], self.is_break[0]))


if __name__ == '__main__':
    Actuator.run("ETHUSDT", '3m', VolumeBreakthroughStrategy)
