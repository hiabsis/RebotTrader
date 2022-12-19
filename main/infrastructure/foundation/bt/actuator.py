import backtrader as bt

from main.infrastructure.rpc.binance.client import BinanceClint
from main.infrastructure.utils.bt import BackTradeUtil


class Actuator:
    @staticmethod
    def create_cerebro(cash=10000.0, commission=0.01, stake=100):
        """
        :param cash: 初始资金
        :param commission: 佣金率
        :param stake: 交易单位大小
        :param strategy: 交易策略
        :return:
        """
        # 加载backtrader引擎
        cerebro = bt.Cerebro()
        # 策略加进来
        cerebro.addsizer(bt.sizers.FixedSize, stake=1)
        # 设置以收盘价成交，作弊模式
        cerebro.broker.set_coc(True)
        cerebro.broker.set_cash(cash)
        # 设置手续费
        cerebro.broker.setcommission(commission=commission)

        return cerebro

    @staticmethod
    def run(symbol, interval, strategy, start_time=None, end_time=None, params=None, cerebro=None):
        if cerebro is None:
            cerebro = Actuator.create_cerebro()
        if params is not None:
            cerebro.addstrategy(strategy=strategy, params=params)
        else:
            cerebro.addstrategy(strategy=strategy)
        BinanceClint.download_kline(symbol, interval)
        data = BackTradeUtil.load_csv(symbol, interval, start=start_time, end=end_time)
        cerebro.adddata(data)
        cerebro.run()
        cerebro.plot()
