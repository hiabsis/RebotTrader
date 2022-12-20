import backtrader as bt
import numpy
import pandas

from main.infrastructure.foundation.logging import log
from main.infrastructure.rpc.binance.client import BinanceClint
from main.infrastructure.utils.bt import BackTradeUtil
from main.infrastructure.utils.date import DateUtil


class Actuator:
    @staticmethod
    def create_cerebro(cash=10000.0, commission=0.01):
        """
        :param cash: 初始资金
        :param commission: 佣金率
        :param stake: 交易单位大小
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
    def run(strategy, data=None, symbol=None, interval=None, start_time=None, end_time=None, params=None, cerebro=None,
            plot=True):
        if cerebro is None:
            cerebro = Actuator.create_cerebro()
        if params is not None:
            cerebro.addstrategy(strategy=strategy, params=params)
        else:
            cerebro.addstrategy(strategy=strategy)
        if data is None:
            BinanceClint.download_kline(symbol, interval)
            data = BackTradeUtil.load_csv(symbol, interval, start=start_time, end=end_time)
        cerebro.adddata(data)
        cerebro.run()
        if plot:
            cerebro.plot()
        return cerebro


class StampDutyCommissionScheme(bt.CommInfoBase):
    """
    本佣金模式下，买入股票仅支付佣金，卖出股票支付佣金和印花税.
    """
    params = (
        ('stamp_duty', 0.005),  # 印花税率
        ('commission', 0.001),  # 佣金率
        ('stocklike', True),
        ('commtype', bt.CommInfoBase.COMM_PERC),
    )

    def _getcommission(self, size, price, pseudoexec):
        """
        If size is greater than 0, this indicates a long / buying of shares.
        If size is less than 0, it idicates a short / selling of shares.
        """

        if size > 0:  # 买入，不考虑印花税
            return size * price * self.p.commission
        elif size < 0:  # 卖出，考虑印花税
            return - size * price * (self.p.stamp_duty + self.p.commission)
        else:
            return 0  # just in case for some reason the size is 0.


class MuActuator:

    @staticmethod
    def run(strategy, interval=None, start_time=None, end_time=None, params=None, cerebro=None,
            plot=True, startcash=10000000):
        if cerebro is None:
            cerebro = bt.Cerebro(stdstats=False)
            cerebro.addobserver(bt.observers.Broker)
            cerebro.addobserver(bt.observers.Trades)
            cerebro.addstrategy(strategy)

            cerebro.broker.setcash(startcash)
            # 防止下单时现金不够被拒绝。只在执行时检查现金够不够。
            cerebro.broker.set_checksubmit(False)
            comminfo = StampDutyCommissionScheme(stamp_duty=0.001, commission=0.001)
            cerebro.broker.addcommissioninfo(comminfo)
        if params is not None:
            cerebro.addstrategy(strategy=strategy, params=params)
        else:
            cerebro.addstrategy(strategy=strategy)
        for symbol in BinanceClint.query_symbols():
            path = BackTradeUtil.local_path(symbol, interval)
            data = numpy.array(pandas.read_csv(path))
            local_date = DateUtil.str2datetime(data[0][0])
            if local_date.timetuple() > DateUtil.str2datetime(start_time).timetuple():
                continue
            data = BackTradeUtil.load_csv(symbol=symbol, interval=interval, start=start_time, end=end_time)
            cerebro.adddata(data, name=symbol)
        cerebro.run()
        if plot:
            cerebro.plot()
        log.info('最终市值: %.2f' % cerebro.broker.getvalue())
        log.info('收益率: %.2f' % ((cerebro.broker.getvalue() - startcash) / startcash * 100))
        return cerebro



