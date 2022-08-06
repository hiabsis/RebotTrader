from base import *
from util import send_text_to_dingtalk


class SimpleMonitorStrategy(bt.Strategy):
    """
    简单预警策略
    """

    def __init__(self, **params):
        self.interval = params['kwargs']['interval']
        self.symbol = params['kwargs']['symbol']
        self.sma = bt.indicator.SimpleMovingAverage(period=50)

    def getNowTime(self):
        return bt.num2date(self.data.datetime[0]).strftime("%Y-%m-%d %H:%M:%S")

    def next(self):
        # 幅度

        pass

    def stop(self):

        if self.data.close[0] > self.data.close[-1] > self.data.close[-2] and self.data.close[
            -2] > self.data.close[-3]:
            trend = "低点不断抬高"
        elif (self.data.high[0] < self.data.high[-1] < self.data.high[-2] and self.data.high[
            -2] < self.data.high[-3]):
            trend = "高点不断下降"
        else:
            trend = "盘整处理当中"
        if self.data.low[0] < self.sma[0] < self.data.high[0]:
            alert_info = "[sma预警][" + self.symbol + "]-[ " + self.interval + "]\n" \
                         + "[time] : " + bt.num2date(self.data.datetime[0]) \
                         + "[sma] : " + str(self.sma[0]) \
                         + "[high] : " + str(self.data.high[0]) \
                         + "[close] : " + str(self.data.close[0]) \
                         + "[trend] : " + trend \
                         + "[info] : " + "价格在sam50附近测试"
            send_text_to_dingtalk(alert_info)
        # # 幅度
        margin = abs((self.data.high[0] - self.data.low[0]) / self.data.close[0] * 100)

        if margin > 2:
            alert_info = "[波动预警] [" + self.symbol + "]-[ " + self.interval + "]\n" \
                         + "[time] : " + self.getNowTime() + "\n" \
                         + "[high] : " + str(self.data.high[0]) + "\n" \
                         + "[close] : " + str(self.data.close[0]) + "\n" \
                         + "[trend] : " + "" + "\n" \
                         + "[margin] : " + str('%.2f' % margin) + "%\n"
            send_text_to_dingtalk(alert_info)

        pass
