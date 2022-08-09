from strategy import *






class KAMAIndicator(bt.Indicator):
    """
    ema通道
        mid = ema(ema(price,rend_period)
        top = ema(ema(price,rend_period)
        bot = ema(ema(price,rend_period)
    """
    lines = ('value',)
    params = (
        ('period', 30),
    )
    # 与价格在同一张图
    plotinfo = dict(subplot=False)

    def __init__(self):
        self.l.value = bt.talib.KAMA(self.data.close, timeperiod=self.p.period)

        super(KAMAIndicator, self).__init__()
