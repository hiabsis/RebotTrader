


# 计算收益评价指标


class TestStrategy(backtrader.Strategy):
    # 设定参数，便于修改
    params = (
        ('maperiod', 60),
    )

    def log(self, txt, dt=None):
        '''
        日志函数：打印结果
        datas[0]：传入的数据，包含日期、OHLC等数据
        datas[0].datetime.date(0)：调用传入数据中的日期列
        '''
        dt = dt or self.datas[0].datetime.date(0)
        # print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # dataclose变量：跟踪当前收盘价
        self.dataclose = self.datas[0].close

        # order变量：跟踪订单状态
        self.order = None
        # buyprice变量：买入价格
        self.buyprice = None
        # buycomm变量：买入时佣金费用
        self.buycomm = None

        # 指标：简单移动平均 MovingAverageSimple【15天】
        self.sma = backtrader.indicators.SimpleMovingAverage(self.datas[0], period=self.params.maperiod)

        # 添加画图专用指标
        backtrader.indicators.ExponentialMovingAverage(self.datas[0], period=25)

        self.my_indicator_kdj = backtrader.indicators.StochasticFull(self.datas[0], period=9)

    def notify_order(self, order):
        '''订单状态通知(order.status)：提示成交状态'''
        if order.status in [order.Submitted, order.Accepted]:
            # 如果订单只是提交状态，那么啥也不提示
            return

        # 检查订单是否执行完毕
        # 注意：如果剩余现金不足，则会被拒绝！
        if order.status in [order.Completed]:
            if order.isbuy():
                # 买入信号记录：买入价、买入费用、买入佣金费用
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            elif order.issell():
                # 卖出信号记录：卖出价、卖出费用、卖出佣金费用
                self.log(
                    'SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))

            # 记录订单执行的价格柱的编号（即长度）
            self.bar_executed = len(self)

        # 如果订单被取消/保证金不足/被拒绝
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # 如果没有查询到订单，则订单为None
        self.order = None

    def notify_trade(self, trade):
        '''交易状态通知：查看交易毛/净利润'''
        if not trade.isclosed:
            return
        # 交易毛利润：trade.pnl、交易净利润：trade.pnlcomm（扣除佣金）
        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))

    # 交易策略主函数
    def next(self):
        # 记录收盘价
        self.log('Close, %.2f' % self.dataclose[0])

        # 检查一下是否有订单被挂起，如果有的话就先不下单
        if self.order:
            return

        # 检查一下目前是否持有头寸，如果没有就建仓
        if not self.position:

            # 如果 K角度>0 且 K>D 且  K<50:
            if (self.my_indicator_kdj.percK[0] > self.my_indicator_kdj.percK[-1]) & (
                    self.my_indicator_kdj.percK[0] > self.my_indicator_kdj.percD[0]) & (
                    self.my_indicator_kdj.percK[0] < 20):
                # 买买买！先记录一下买入价格（收盘价）
                self.log('BUY CREATE, %.2f' % self.dataclose[0])
                # 更新订单状态：buy()：开仓买入，买入价是下一个数据，即【开盘价】
                self.order = self.buy()
        else:
            # 如果已经建仓，并持有头寸，则执行卖出指令
            # 如果 K角度<0 且 K<D 且 K>70:
            if (self.my_indicator_kdj.percK[0] < self.my_indicator_kdj.percK[-1]) & (
                    self.my_indicator_kdj.percK[0] < self.my_indicator_kdj.percD[0]):
                # 卖!卖!卖!
                self.log('SELL CREATE, %.2f' % self.dataclose[0])
                # 更新订单状态：sell()：平仓卖出，卖出价是下一个数据，即【开盘价】
                self.order = self.sell()


