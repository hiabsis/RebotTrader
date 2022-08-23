"""
肯特纳通道
"""
import backtrader as bt


class KeltnerChannelIndex(bt.Indicator):
    """
    肯特纳通道(指标)
    上轨=中轨+2*ATR
    下轨=中轨-2*ATR
    最初中轨用到的是10SMA
    优化后改为中线EMA的周期选择20，ATR周期是10
    """
    params = (
        ('ema', 50),  # EMA的周期
        ('atr', 30),  # ATR周期是10
    )
    lines = ('mid',  # 中轨
             'top',  # 上轨
             'bot',  # 下轨
             )

    plotinfo = dict(subplot=False)

    def __init__(self, **kwargs):
        # 价格过滤
        # price = (self.data.close + self.data.open + self.data.low) / 4
        ema = bt.ind.EMA(period=self.p.ema)
        atr = bt.ind.ATR(period=self.p.atr, movav=bt.ind.EMA)
        # 计算上中下轨线
        self.l.mid = ema
        self.l.top = ema + 2 * atr
        self.l.bot = ema - 2 * atr
        super(KeltnerChannelIndex, self).__init__()


class KeltnerChannelStrategy(bt.Strategy):
    """
    基于 肯特纳通道策略
    次要趋势规则是使用每日趋势作为交易的指南，
    交易点位居于最近高点的上方，那么，其显示的是上升趋势；
    如果在天图当中，最近的交易点位居于最近低点之下，那么，相应的趋势方向就会发生改变，否则，这种次要趋势将保持不变。
    当次要趋势转而向上时，买入；
    当次要趋势转而向下时，卖出，如此则需要不断地进场、平仓或反向做单
    """
    params = dict(
        is_log=False,
        kc_ema=150,
        kc_atr=150,
    )

    def init(self, params):
        if params is None:
            return
        if 'kc_ema' in params:
            self.p.kc_ema = params['kc_ema']
        if 'kc_atr' in params:
            self.p.kc_atr = params['kc_atr']

    def __init__(self, params=None):
        self.init(params)
        self.kc = KeltnerChannelIndex(ema=self.p.kc_ema, atr=self.p.kc_atr)
        self.order = None

    def log(self, txt, dt=None):
        if self.p.is_log:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s,%s' % (dt.isoformat(), txt))

    def next(self):

        self.log(1)
        if self.position.size > 0:
            # 突破下轨道
            if self.data.close[-1] < self.kc.bot[-1]:
                self.close()
        elif self.position.size < 0:
            #  突破上轨
            if self.data.open[-1] > self.kc.top[-1]:
                self.close()
        else:
            if self.data.open[-1] > self.kc.top[-1]:
                size = self.broker.getcash() / self.data.open[0]
                self.order = self.buy(size=int(size))

            if self.data.close[-1] < self.kc.bot[-1]:
                size = self.broker.getcash() / self.data.open[0]
                self.order = self.sell(size=int(size))
