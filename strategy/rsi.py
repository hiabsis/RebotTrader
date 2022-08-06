from base import *


class RSIStrategy(BaseStrategy):
    def __init__(self):
        self.rsi = bt.indicators.RSI(period=7)  # RSI indicator
        self.sma = bt.indicators.SMA(period=200)

    def next(self):
        # 检查是否还有订单未处理，有的话等等
        if self.order:
            return

        # Check if we are in the market
        if not self.position:
            # 大于均线就买
            if self.dataclose[0] > self.sma[0]:
                # BUY, BUY, BUY!!! (with all possible default parameters)
                self.log('BUY CREATE, %.2f' % self.dataclose[0])
                # Keep track of the created order to avoid a 2nd order
                self.order = self.buy()
        else:

            if self.dataclose[0] < self.sma[0]:
                # 小于均线卖卖卖！
                self.log('SELL CREATE, %.2f' % self.dataclose[0])
                self.order = self.close()
