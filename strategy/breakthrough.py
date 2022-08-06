from base import *


class BreakthroughStrategy(Strategy):
    """
    """
    params = dict(
        break_through=0.04,  # 上涨幅度
        callback=0.02,  # 价格回调比例
        period=100,  # sma周期
        down_day=5,  # 连续下跌天数
        stop_loss=0.05,  # 止损比例
        take_profit=0.1,  # 止盈比例
        validity_day=3,  # 订单有效期
        expired_day=1000,  # 订单失效期
    )

    def notify_order(self, order):
        if order.status == order.Completed:
            self.holdstart = len(self)
        if not order.alive() and order.ref in self.orefs:
            self.orefs.remove(order.ref)

    def __init__(self):
        self.holdstart = None
        self.dataclose = self.datas[0].close  # 收盘价
        self.sma = bt.ind.SMA(period=self.p.period, plot=True)  # SMA
        self.orefs = list()  # order列表，用于存储尚未执行完成的订单

    def next(self):
        # 有尚未执行的订单
        if self.orefs:
            return
            # 尚未进场
            # 获取近几日收盘价用于判断是否连续下跌
        last_closes = list()
        for i in range(1, self.p.down_day + 1):
            last_closes.append(self.dataclose[-i])
        if not self.position:

            # 判断十分突破
            is_break = False
            if self.dataclose[0] > self.dataclose[-1] \
                    and (self.data.high[0] - self.dataclose[0]) / self.dataclose[0] > self.p.break_through:
                is_break = True
            # 连续N日下跌 在 sma上方
            if last_closes == sorted(last_closes, reverse=False) and is_break and self.dataclose[0] > self.sma[0]:
                p1 = self.dataclose[0] * (1.0 - self.p.callback)
                p2 = p1 - self.p.stop_loss * p1
                p3 = p1 + self.p.take_profit * p1
                # 计算订单有效期
                validity_day = datetime.timedelta(self.p.validity_day)
                expired_day = valid3 = datetime.timedelta(self.p.expired_day)
                size = min(self.broker.getcash() / self.data.high[0], self.data.volume)
                os = self.buy_bracket(size=size,
                                      price=p1, valid=validity_day,
                                      stopprice=p2, stopargs=dict(valid=expired_day),
                                      limitprice=p3, limitargs=dict(valid=valid3), )
                # 保存激活的的订单
                self.orefs = [o.ref for o in os]


class BreakThroughStrategyOptimizer:
    # 策略参数
    params = dict(
        break_through=0.04,  # 上涨幅度
        callback=0.02,  # 价格回调比例
        period=100,  # 周期
        down_day=5,  # 连续下跌天数
        stop_loss=0.05,  # 止损比例
        take_profit=0.1,  # 止盈比例
    )
    # 调优参数范围
    optimize_params = dict(
        break_through=[0.03, 0.04],  # 上涨幅度
        callback=[0.02, 0.08],  # 价格回调比例
        period=[50, 200],  #
        down_day=[3, 15],  # 连续下跌天数
        stop_loss=[0.05, 0.2],  # 止损比例
        take_profit=[0.05, 0.2],  # 止盈比例
    )

    # 调优参数范围
    optimize_cerebro_params = dict(
        period=[50, 200],  #
        down_day=[3, 15],  # 连续下跌天数
        stop_loss=[0.05, 0.2],  # 止损比例
        take_profit=[0.05, 0.2],  # 止盈比例
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
        self.params_optimize(
            break_through=self.params['break_through'],
            callback=self.params['callback'],
            down_day=self.params['down_day'],
            period=self.params['period'],
            stop_loss=self.params['stop_loss'],
            take_profit=self.params['take_profit'],
            is_show_plot=False
        )
        return self.cerebro.broker.getvalue()

    def params_optimize(self, break_through, callback, down_day, period, stop_loss=0.05, take_profit=0.01):
        """
        参数优化
        :param down_day: 连续下跌天数
        :param period: 周期
        :param break_through: 突破比例
        :param callback: 价格回撤
        :param stop_loss: 盈亏比 止损
        :param take_profit: 盈亏比 止盈
        """
        self.params = dict(
            break_through=break_through,  # 上涨幅度
            callback=callback,  # 价格回调比例
            period=period,  # 周期
            down_day=down_day,  # 连续下跌天数
            stop_loss=stop_loss,  # 止损比例
            take_profit=take_profit,  # 止盈比例
        )
        kines = self.get_data()
        self.cerebro = create_cerebro(self.cash)
        self.cerebro.adddata(kines)
        self.cerebro = add_breakthrough_strategy(self.cerebro, self.params)

        self.cerebro.run()
        rate = self.cerebro.broker.getvalue() / self.cash
        if self.cerebro.broker.getvalue() != self.cash:
            print(self.cerebro.broker.getvalue())
        if rate > 5 or self.is_show_params:
            self.log(f"rate: {rate} ")
            self.log(f"break_through:{break_through}")
            self.log(f"callback: {callback}")
            self.log(f"period: {period}")
            self.log(f"down_day: {down_day}")
            self.log(f"stop_loss: {stop_loss}")
            self.log(f"take_profit: {take_profit}")
            self.log(f"asset: {(self.cerebro.broker.getvalue())}")
            self.log(f"params:{self.params}")
        return self.cerebro.broker.getvalue()

    def run(self):
        opt = optunity.maximize(
            f=self.params_optimize,
            num_evals=self.event_num,
            solver_name='particle swarm',
            break_through=self.optimize_params['break_through'],
            callback=self.optimize_params['callback'],
            down_day=self.optimize_params['down_day'],
            period=self.optimize_params['period'],
            stop_loss=self.optimize_params['stop_loss'],
            take_profit=self.optimize_params['take_profit']
        )
        optimal_pars, details, _ = opt  # optimal_pars 最优参数组合
        self.params = optimal_pars
        print(self.params)

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


def add_breakthrough_strategy(c: Cerebro, params=None):
    """
    设置策略参数
    :param c:
    :param params:
    :return:
    """
    if params is None:
        return c.addstrategy(BreakthroughStrategy)
    c.addstrategy(BreakthroughStrategy,
                  break_through=params['break_through'],
                  callback=params['callback'],
                  period=int(params['period']),
                  down_day=int(params['down_day']),
                  stop_loss=params['stop_loss'],
                  take_profit=params['take_profit'])
    return c




