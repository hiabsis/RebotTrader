"""
公共部分代码
"""
import backtrader as bt


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
            return size * price * (self.p.stamp_duty + self.p.commission)
        else:
            return 0  # just in case for some reason the size is 0.


class BaoStockDayGenericCSDataExtend(bt.feeds.GenericCSVData):
    """
    日线级别的数据
    """
    # 增加线
    lines = ("amount", 'adjustflag', 'turn', 'tradestatus', 'pctChg', 'isST')
    params = (('amount', 0),  # 成交额
              ('adjustflag', 0),  # 是否复权
              ('turn', 0),  # 换手率
              ('tradestatus', 0),  # 交易状态 1：正常交易 0：停牌
              ('pctChg', 0),  # 涨跌幅
              ('isST', 3),)  # 是否ST	1是，0否


class BaoStockMinuteGenericCSDataExtend(bt.feeds.GenericCSVData):
    """
    分钟级别的数据
    """
    # 增加线
    lines = ("amount", 'adjustflag')
    params = (('amount', 0),  # 成交额
              ('adjustflag', 0),  # 是否复权
              )



