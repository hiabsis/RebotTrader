#!/usr/bin389/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
###############################################################################
#
# 该程序是海龟策略实现
#
###############################################################################
import os

from base import *

# 编写海龟策略
from continuous_decline import ContinuousDeclineStrategyOptimizer


class TurtleTradingStrategy(bt.Strategy):
    name = "海龟策略"
    params = dict(
        N1=40,  # 唐奇安通道上轨的t
        N2=30,  # 唐奇安通道下轨的t
        ATR_T=40,  # ATR的周期T
        printlog=False,
    )

    def log(self, txt, dt=None, doprint=False):
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print(f'{dt.isoformat()},{txt}')

    def __init__(self):
        self.order = None
        self.buy_count = 0  # 记录买入次数
        self.last_price = 0  # 记录买入价格
        # 第一个标的沪深300主力合约的close、high、low 行情数据
        self.close = self.datas[0].close
        self.high = self.datas[0].high
        self.low = self.datas[0].low
        # 计算唐奇安通道上轨：过去最高价
        self.DonchianH = bt.ind.Highest(self.high(-1), period=self.p.N1, subplot=True)
        # 计算唐奇安通道下轨：过去最低价
        self.DonchianL = bt.ind.Lowest(self.low(-1), period=self.p.N2, subplot=True)
        # 生成唐奇安通道上轨突破：close>DonchianH，取值为1.0；反之为 -1.0
        self.CrossoverH = bt.ind.CrossOver(self.close(0), self.DonchianH, subplot=False)
        # 生成唐奇安通道下轨突破:
        self.CrossoverL = bt.ind.CrossOver(self.close(0), self.DonchianL, subplot=False)
        # ATR
        self.ATR = bt.talib.ATR(self.high, self.low, self.close, timeperiod=self.p.ATR_T, subplot=True)

    def next(self):
        # 如果还有订单在执行中，就不做新的仓位调整
        if self.order:
            return
            # 如果当前持有多单
        if self.position.size > 0:
            # 多单加仓:价格上涨了买入价的0.5的ATR且加仓次数少于等于3次
            if self.datas[0].close > self.last_price + 0.5 * self.ATR[0] and self.buy_count <= 4:
                #                 print('if self.datas[0].close >self.last_price + 0.5*self.ATR[0] and self.buy_count <= 4:')
                #                 print('self.buy_count',self.buy_count)
                # 计算建仓单位：self.ATR*期货合约乘数300*保证金比例0.1
                self.buy_unit = max((self.broker.getvalue() * 0.005) / (self.ATR * 300 * 0.1), 1)
                self.buy_unit = int(self.buy_unit)  # 交易单位为手
                # self.sizer.p.stake = self.buy_unit
                self.order = self.buy(size=self.buy_unit)
                self.last_price = self.position.price  # 获取买入价格
                self.buy_count = self.buy_count + 1
            # 多单止损：当价格回落2倍ATR时止损平仓
            elif self.datas[0].close < (self.last_price - 2 * self.ATR[0]):
                #                 print('elif self.datas[0].close < (self.last_price - 2*self.ATR[0]):')
                self.order = self.sell(size=abs(self.position.size))
                self.buy_count = 0
            # 多单止盈：当价格突破10日最低点时止盈离场 平仓
            elif self.CrossoverL < 0:
                #                 print('self.CrossoverL < 0')
                self.order = self.sell(size=abs(self.position.size))
                self.buy_count = 0

                # 如果当前持有空单
        elif self.position.size < 0:
            # 空单加仓:价格小于买入价的0.5的ATR且加仓次数少于等于3次
            if self.datas[0].close < self.last_price - 0.5 * self.ATR[0] and self.buy_count <= 4:
                #                 print('self.datas[0].close<self.last_price-0.5*self.ATR[0] and self.buy_count <= 4')
                # 计算建仓单位：self.ATR*期货合约乘数300*保证金比例0.1
                self.buy_unit = max((self.broker.getvalue() * 0.005) / (self.ATR * 300 * 0.1), 1)
                self.buy_unit = int(self.buy_unit)  # 交易单位为手
                # self.sizer.p.stake = self.buy_unit
                self.order = self.sell(size=self.buy_unit)
                self.last_price = self.position.price  # 获取买入价格
                self.buy_count = self.buy_count + 1
                # 空单止损：当价格上涨至2倍ATR时止损平仓
            elif self.datas[0].close < (self.last_price + 2 * self.ATR[0]):
                #                 print('self.datas[0].close < (self.last_price+2*self.ATR[0])')
                self.order = self.buy(size=abs(self.position.size))
                self.buy_count = 0
            # 多单止盈：当价格突破20日最高点时止盈平仓
            elif self.CrossoverH > 0:
                #                 print('self.CrossoverH>0')
                self.order = self.buy(size=abs(self.position.size))
                self.buy_count = 0

        else:  # 如果没有持仓，等待入场时机
            # 入场: 价格突破上轨线且空仓时，做多
            if self.CrossoverH > 0 and self.buy_count == 0:
                #                 print('if self.CrossoverH > 0 and self.buy_count == 0:')
                # 计算建仓单位：self.ATR*期货合约乘数300*保证金比例0.1
                self.buy_unit = max((self.broker.getvalue() * 0.005) / (self.ATR * 300 * 0.1), 1)
                self.buy_unit = int(self.buy_unit)  # 交易单位为手
                self.order = self.buy(size=self.buy_unit)
                self.last_price = self.position.price  # 记录买入价格
                self.buy_count = 1  # 记录本次交易价格
            # 入场: 价格跌破下轨线且空仓时，做空
            elif self.CrossoverL < 0 and self.buy_count == 0:
                #                 print('self.CrossoverL < 0 and self.buy_count == 0')
                # 计算建仓单位：self.ATR*期货合约乘数300*保证金比例0.1
                self.buy_unit = max((self.broker.getvalue() * 0.005) / (self.ATR * 300 * 0.1), 1)
                self.buy_unit = int(self.buy_unit)  # 交易单位为手
                self.order = self.sell(size=self.buy_unit)
                self.last_price = self.position.price  # 记录买入价格
                self.buy_count = 1  # 记录本次交易价格

    # 打印订单日志
    def notify_order(self, order):
        order_status = ['Created', 'Submitted', 'Accepted', 'Partial',
                        'Completed', 'Canceled', 'Expired', 'Margin', 'Rejected']
        # 未被处理的订单
        if order.status in [order.Submitted, order.Accepted]:
            self.log('ref:%.0f, name: %s, Order: %s' % (order.ref,
                                                        order.data._name,
                                                        order_status[order.status]))
            return
        # 已经处理的订单
        if order.status in [order.Partial, order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, status: %s, ref:%.0f, name: %s, Size: %.2f, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order_status[order.status],  # 订单状态
                     order.ref,  # 订单编号
                     order.data._name,  # 股票名称
                     order.executed.size,  # 成交量
                     order.executed.price,  # 成交价
                     order.executed.value,  # 成交额
                     order.executed.comm))  # 佣金
            else:  # Sell
                self.log(
                    'SELL EXECUTED, status: %s, ref:%.0f, name: %s, Size: %.2f, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order_status[order.status],
                     order.ref,
                     order.data._name,
                     order.executed.size,
                     order.executed.price,
                     order.executed.value,
                     order.executed.comm))

        elif order.status in [order.Canceled, order.Margin, order.Rejected, order.Expired]:
            # 订单未完成
            self.log('ref:%.0f, name: %s, status: %s' % (
                order.ref, order.data._name, order_status[order.status]))

        self.order = None

    def notify_trade(self, trade):
        # 交易刚打开时
        if trade.justopened:
            self.log('Trade Opened, name: %s, Size: %.2f,Price: %.2f' % (
                trade.getdataname(), trade.size, trade.price))
        # 交易结束
        elif trade.isclosed:
            self.log('Trade Closed, name: %s, GROSS %.2f, NET %.2f, Comm %.2f' % (
                trade.getdataname(), trade.pnl, trade.pnlcomm, trade.commission))
        # 更新交易状态
        else:
            self.log('Trade Updated, name: %s, Size: %.2f,Price: %.2f' % (
                trade.getdataname(), trade.size, trade.price))

    def stop(self):

        self.log(f'(组合线:{self.p.N1},{self.p.N2},{self.p.ATR_T}) \
        期末总资金: {self.broker.getvalue():.2f}', doprint=True)


class TurtleTradingStrategyOptimizer(ContinuousDeclineStrategyOptimizer):
    name = "海龟策略"
    params = dict(
        N1=40,  # 唐奇安通道上轨的t
        N2=30,  # 唐奇安通道下轨的t,
        ATR_T=10,  # ATR周期

    )

    def get_name(self):
        return self.name

    # 调优参数范围
    optimize_params = dict(
        N1=[5, 50],  # 唐奇安通道上轨的t
        N2=[10, 100],  # 唐奇安通道下轨的t
        ATR_T=[4, 40],  # ATR周期
    )

    def get_optimize_total_assets(self):
        """
        获取最优策略回测后的总资产
        :return:
        """
        self.params_optimize(
            N1=self.params['N1'],
            N2=self.params['N2'],
            ATR_T=self.params['ATR_T']
        )
        return self.cerebro.broker.getvalue()

    def params_optimize(self, N1, N2, ATR_T):
        """
        参数优化
        """
        self.params = dict(
            N1=N1,  # 上涨幅度
            N2=N2,  # 价格回调比例
            ATR_T=ATR_T,  # 周期
        )
        kines = self.get_data()
        self.cerebro = create_cerebro(self.cash)
        self.cerebro.adddata(kines)
        self.cerebro = add_turtle_trading_strategy(self.cerebro, self.params)

        self.cerebro.run()
        rate = self.cerebro.broker.getvalue() / self.cash
        if rate > 5 or self.is_show_params:
            self.log()
            self.log(f"rate: {rate} ")
            self.log(f"N1:{N1}")
            self.log(f"N2: {N2}")
            self.log(f"ATR_T: {ATR_T}")
            self.log(f"asset: {(self.cerebro.broker.getvalue())}")
            self.log(f"params:{self.params}")
            self.log()
        return self.cerebro.broker.getvalue()

    def run(self):
        opt = optunity.maximize(
            f=self.params_optimize,
            num_evals=self.event_num,
            solver_name='particle swarm',
            N1=self.optimize_params['N1'],
            N2=self.optimize_params['N2'],
            ATR_T=self.optimize_params['ATR_T'],
        )
        optimal_pars, details, _ = opt  # optimal_pars
        self.params = optimal_pars
        print("最优参数组合")
        print(self.params)
        print("总资金")
        print(self.get_optimize_total_assets())


def add_turtle_trading_strategy(c: Cerebro, params=None):
    """
    设置策略参数
    :param c:
    :param params:
    :return:
    """
    if params is None:
        c.addstrategy(TurtleTradingStrategy)
    else:
        c.addstrategy(TurtleTradingStrategy,
                      N1=int(params['N1']),
                      N2=int(params['N2']),
                      ATR_T=int(params['ATR_T']))
    return c


if __name__ == '__main__':
    path = "/static/data"
    # os.listdir()方法获取文件夹名字，返回数组
    file_name_list = os.listdir(path)
    for i in file_name_list:
        file_path = path + "\\" + i
        print(file_path)
        app = MainApp()
        date = load_csv_data(file_path)
        app.add_data(date)
        app.set_fuc(add_turtle_trading_strategy)
        # app.run()
        opt = TurtleTradingStrategyOptimizer()
        # opt.set_data(date)
        opt.set_event_num(500)
        app.set_optimizer(opt)
        # app.run_optimizer()
        app.verify_optimizer(path=file_path)
    # app.add_strategy(strategy=ContinuousDeclineStrategy)
