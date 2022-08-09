from strategy import *


class EmaBandIndicator(bt.Indicator):
    """
    ema通道
        mid = ema(ema(price,rend_period)
        top = ema(ema(price,rend_period)
        bot = ema(ema(price,rend_period)
    """
    lines = ('mid', 'top', 'bot')
    params = (
        ('rend_period', 30),
        ('top_ratio', 1.1),
        ('low_ratio', 0.9),)
    # 与价格在同一张图
    plotinfo = dict(subplot=False)

    def __init__(self):
        ema = bt.ind.EMA(self.data, period=self.p.rend_period)
        # 计算上中下轨线
        self.l.mid = bt.ind.EMA(ema, period=self.p.rend_period)
        self.l.top = bt.ind.EMA(self.mid * self.p.top_ratio,
                                period=self.p.rend_period)
        self.l.bot = bt.ind.EMA(self.mid * self.p.low_ratio,
                                period=self.p.rend_period)
        super(EmaBandIndicator, self).__init__()
