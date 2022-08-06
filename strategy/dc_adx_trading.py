# !/usr/bin389/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
###############################################################################
#
# 该程序基于唐奇安通道 + ADX 开发策略
#
###############################################################################
from base import *


class D_ADX_TradingStrategy(BaseStrategy):
    name = "于唐奇安通道 + ADX策略"
    """
    海龟策略
    """
    params = dict(
        N1=40,  # 唐奇安通道上轨的t
        N2=30,  # 唐奇安通道下轨的t
        N3=25,  # ADX的强度值
        N4=20,  # ADX的时间周期参数
    )



    def __init__(self):
        self.buy_unit = None
        self.order = None
        self.buy_count = 0  # 记录买入次数
        self.last_price = 0  # 记录买入价格
        self.close = self.datas[0].close
        self.high = self.datas[0].high
        self.low = self.datas[0].low
        # 计算唐奇安通道上轨：过去20日的最高价
        self.DonchianH = bt.ind.Highest(self.high(-1), period=int(self.p.N1), subplot=True)
        # 计算唐奇安通道下轨：过去10日的最低价
        self.DonchianL = bt.ind.Lowest(self.low(-1), period=int(self.p.N2), subplot=True)
        # 计算唐奇安通道中轨
        self.DonchianM = (self.DonchianH + self.DonchianL) / 2

        # 生成唐奇安通道上轨突破：close>DonchianH，取值为1.0；反之为 -1.0
        self.CrossoverH = bt.ind.CrossOver(self.close(0), self.DonchianH, subplot=False)
        # 生成唐奇安通道下轨突破:
        self.CrossoverL = bt.ind.CrossOver(self.close(0), self.DonchianL, subplot=False)
        # 生成唐奇安通道中轨突破:
        self.CrossoverM = bt.ind.CrossOver(self.close(0), self.DonchianM, subplot=False)

        # 计算 ADX，直接调用 talib
        self.ADX = bt.talib.ADX(self.high, self.low, self.close, timeperiod=int(self.p.N4), subplot=True)

    #         self.log(self.ADX[-1],doprint=True)
    def next(self):
        #         self.log(self.ADX[0],doprint=True)
        # 如果还有订单在执行中，就不做新的仓位调整
        if self.order:
            return

            # 如果当前持有多单
        if self.position:
            # 平仓设置
            if self.CrossoverM < 0 or self.ADX[0] < self.ADX[-1]:
                self.order = self.sell(size=abs(self.position.size))
                self.buy_count = 0

        else:  # 如果没有持仓，等待入场时机
            # 入场: 价格突破上轨线且空仓时，做多
            if self.CrossoverH > 0 and self.buy_count == 0 and self.ADX[0] > self.ADX[-1] > int(
                    self.p.N3):
                self.buy_unit = min(int(self.broker.getcash() / self.high[0]), self.data.volume[0])

                self.order = self.buy(size=self.buy_unit)
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

        self.log(f'(组合线：{self.p.N1},{self.p.N2},{self.p.N3},{self.p.N4}); 期末总资金: {self.broker.getvalue():.2f}',
                 doprint=True)


class D_ADX_TradingStrategyOptimizer(Optimizer):
    # 策略参数
    params = dict(
        N1=0.02,
        N2=100,
        N3=5,
        N4=0.05,

    )
    # 调优参数范围
    optimize_params = dict(
        N1=[1, 100],  # 价格回调比例
        N2=[1, 200],  #
        N3=[5, 100],  # 连续下跌天数
        N4=[5, 100]
    )

    def __init__(self):
        # 数据
        self.data = None
        # 持有现金
        self.cash = 10000.0
        # 资产
        self.value = 10000.0
        self.cerebro = None
        # 迭代次数
        self.event_num = 500
        # 是否显示迭代参数
        self.is_show_params = False

    def log(self, txt):
        """
        日志记录
        :param txt:
        :return:
        """
        print(txt)

    def set_cash(self, cash):
        self.cash = cash

    def set_event_num(self, event_num):
        self.event_num = event_num

    def set_data(self, feed_data):
        """
        设置数据
        :param feed_data:
        :return:
        """
        self.data = feed_data

    def get_data(self):
        """
        获取数据
        :return:
        """
        return self.data

    def get_optimize_total_assets(self):
        """
        获取最优策略回测后的总资产
        :return:
        """
        return self.params_optimize(N1=self.params['N1'], N2=self.params['N2'], N3=self.params['N3'],
                                    N4=self.params['N4'])

    def params_optimize(self, N1, N2, N3, N4):
        """
        参数优化

        """
        self.params = dict(
            N1=N1,
            N2=N2,
            N3=N3,
            N4=N4,
        )
        kines = self.get_data()
        self.cerebro = create_cerebro(self.cash)
        self.cerebro.adddata(kines)
        self.cerebro = add_D_ADX_trading_strategy(self.cerebro, self.params)

        self.cerebro.run()
        rate = self.cerebro.broker.getvalue() / self.cash
        if rate > 1.2 or self.is_show_params:
            self.log(f"rate: {rate} ")
            self.log(f"params:{self.params}")
            self.log("")
        return self.cerebro.broker.getvalue()

    def run(self):
        opt = optunity.maximize(
            f=self.params_optimize,
            num_evals=self.event_num,
            solver_name='particle swarm',
            N1=self.optimize_params['N1'],
            N2=self.optimize_params['N2'],
            N3=self.optimize_params['N3'],
            N4=self.optimize_params['N4'],
        )
        optimal_pars, details, _ = opt  # optimal_pars 最优参数组合
        self.params = optimal_pars
        print(self.params)
        message = "唐纳德+ADX 策略+\n" + "参数：\n" + dumps(
            self.params) + f"\n 初始资金： {self.cash}" + "\n期末资金：" + self.get_optimize_total_assets()
        send_text_to_dingtalk(message)

    def get_trader_info(self):
        return 'Starting Portfolio Value: %.2f \n' % self.cash \
               + 'Final Portfolio Value: %.2f \n' % self.cerebro.broker.getvalue() \
               + f'Final Portfolio Percentage: {100.0 * self.cerebro.broker.getvalue() / self.cash} %\n' \
               + f'PARAMS {self.params}\n'

    def get_optimal_parameters(self):
        """
        获取最优参数
        :return:
        """
        return self.params


def add_D_ADX_trading_strategy(c: Cerebro, params: dict):
    if params is None:
        c.addstrategy(D_ADX_TradingStrategy)
    else:
        c.addstrategy(D_ADX_TradingStrategy, N1=params["N1"], N2=params['N2'], N3=params['N3'], N4=params['N4'])
    return c


if __name__ == '__main__':
    path = "/static/data/BTCUSDT_1h.csv"
    data = load_csv_data(path)
    app = MainApp()
    app.set_cash(10 * 1000)
    app.add_data(data)
    app.add_strategy(func=add_D_ADX_trading_strategy)
    app.run()
