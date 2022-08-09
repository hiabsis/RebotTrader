from __future__ import (absolute_import, division, print_function, unicode_literals)
import datetime  # 用于datetime对象操作
import os.path  # 用于管理路径
import sys  # 用于在argvTo[0]中找到脚本名称
import backtrader as bt  # 引入backtrader框架
from util import data_util


# 自定义指标
class NegativeIndicator(bt.Indicator):
    lines = ('buy_sig',)
    params = (('ma_period', 10), ('up_period', 3))

    def __init__(self):
        self.addminperiod(self.p.ma_period)
        ma = bt.ind.SMA(period=self.p.ma_period, plot=True)
        # 买入条件
        # 收阴线
        self.l.buy_sig = bt.And(self.data.close < self.data.open,
                                # 收在均线上方
                                self.data.close > ma,
                                # 均线向上
                                ma == bt.ind.Highest(ma, period=self.p.up_period)
                                )


# 创建策略
class St(bt.Strategy):
    params = dict(
        stoptype=bt.Order.StopTrail,
        trailamount=0.0,
        trailpercent=0.05,
    )

    def __init__(self):
        # 买入条件
        self.buy_sig = NegativeIndicator().buy_sig
        # # 为了在最后图表中显示均线
        # bt.ind.SMA(period=NegativeIndicator().p.ma_period)
        # self.order = None

    # def notify_order(self, order):
    #     if order.status in [order.Completed, order.Expired]:
    #         self.order = None
    #
    # def next(self):
    #     # 无场内资产
    #     if not self.position:
    #         # 未提交买单
    #         if None == self.order:
    #             # 到达了买入条件
    #             if self.buy_sig:
    #                 self.order = self.buy()
    #     elif self.order is None:
    #         # 提交stoptrail订单
    #         self.order = self.sell(exectype=self.p.stoptype,
    #                                trailamount=self.p.trailamount,
    #                                trailpercent=self.p.trailpercent)


cerebro = bt.Cerebro()  # 创建cerebro
# 先找到脚本的位置，然后根据脚本与数据的相对路径关系找到数据位置
# 这样脚本从任意地方被调用，都可以正确地访问到数据
data = data_util.get_local_generic_csv_data("ETH", '1h')
# modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
# datapath = os.path.join(modpath, '../TQDat/day/stk/000001.csv')
# # 创建价格数据
# data = bt.feeds.GenericCSVData(
#     dataname=datapath,
#     fromdate=datetime.datetime(2018, 1, 1),
#     todate=datetime.datetime(2020, 3, 31),
#     nullvalue=0.0,
#     dtformat=('%Y-%m-%d'),
#     datetime=0,
#     open=1,
#     high=2,
#     low=3,
#     close=4,
#     volume=5,
#     openinterest=-1
# )
# 在Cerebro中添加价格数据
cerebro.adddata(data)
# 设置启动资金
cerebro.broker.setcash(100000.0)
# 设置交易单位大小
cerebro.addsizer(bt.sizers.FixedSize, stake=1000)
# 设置佣金为千分之一
cerebro.broker.setcommission(commission=0.001)
cerebro.addstrategy(St)  # 添加策略
cerebro.run()  # 遍历所有数据
# 打印最后结果
print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
cerebro.plot(style='candlestick')  # 绘图
