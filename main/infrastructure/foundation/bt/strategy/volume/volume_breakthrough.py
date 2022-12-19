"""
交易量突破策略
"""

import backtrader as bt

from main.infrastructure.utils.bt import BackTradeUtil


class VolumeBreakthroughIndex(bt.Indicator):
    lines = (
        'direction',  # 涨跌方向 1 多 -1
        'is_break',  # 交易量是否突破
    )
    params = (
        # 放量值
        ('break_volume', 4),
        # 周期
        ('period', 5)

    )  #
    plotinfo = dict(
        plot=True,
        subplot=True,  # 与价格在同一张图
        plotname='交易量突破',
    )

    def __init__(self):
        # ema: 交易量
        volume_ema = bt.ind.EMA(self.data.volume, period=self.p.period)
        open_ema = bt.ind.EMA(self.data.open, period=self.p.period)
        close_ema = bt.ind.EMA(self.data.close, period=self.p.period)
        self.direction = bt.ind.If(open_ema >= close_ema, 1, -1)
        self.is_break = bt.ind.If(self.data.volume >= volume_ema * self.p.break_volume, 1, 0)
        super(VolumeBreakthroughIndex, self).__init__()


class VolumeBreakthroughStrategy(bt.Strategy):
    def __init__(self):
        index = VolumeBreakthroughIndex()
        self.is_break = index.is_break
        self.direction = index.direction


if __name__ == '__main__':
    csv = BackTradeUtil.load_csv("ETHUSDT", "5m")
