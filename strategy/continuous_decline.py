import os

from base import *


def add_continuous_decline_strategy(c: Cerebro, params=None):
    """
    设置策略参数
    :param c:
    :param params:
    :return:
    """
    if params is None:
        c.addstrategy(ContinuousDeclineStrategy)
    else:
        c.addstrategy(ContinuousDeclineStrategy,
                      callback=params['callback'],
                      period=int(params['period']),
                      down_day=int(params['down_day']),
                      stop_loss=params['stop_loss'],
                      take_profit=params['take_profit'])
    return c


class ContinuousDeclineStrategy(BaseStrategy):
    """
    阴跌策略
    """
    params = dict(
        callback=0.01,  # 价格回调比例
        period=133,
        down_day=6,
        stop_loss=133,  # 止损比例
        take_profit=0.15,  # 止盈比例
        limdays=3,
        limdays2=1000,
        hold=10,
    )

    def __init__(self):
        self.holdstart = None
        self.dataclose = self.datas[0].close
        self.sma = bt.ind.SMA(period=self.p.period, plot=False)
        self.order_list = list()

    def next(self):
        if self.order_list:  # order列表，用于存储尚未执行完成的订单
            return  # 有尚未执行的订单
        # 尚未进场
        if not self.position:
            # 获取近几日收盘价用于判断是否连续上涨
            last_closes = list()
            for i in range(self.p.down_day + 1):
                last_closes.append(self.dataclose[-i])

            # 连续N日下跌
            if last_closes == sorted(last_closes, reverse=True):
                close = self.dataclose[0]
                p1 = close * (1.0 - self.p.callback)
                p2 = p1 - self.p.stop_loss * close
                p3 = p1 + self.p.take_profit * close
                # 计算订单有效期
                valid1 = datetime.timedelta(self.p.limdays)
                valid2 = valid3 = datetime.timedelta(self.p.limdays2)
                size = min(self.broker.getcash() / self.sma[0], self.data.volume[0])
                # 使用bracket orders设置买入卖出
                if size == 0:
                    size = 1
                os = self.buy_bracket(size=size,
                                      price=p1,
                                      valid=valid1,
                                      stopprice=p2,
                                      stopargs=dict(valid=valid2),
                                      limitprice=p3,
                                      limitargs=dict(valid=valid3), )
                # 保存激活的的订单
                self.orefs = [o.ref for o in os]

    @staticmethod
    def set_params(c: Cerebro, params):
        if params is None:
            c.addstrategy(ContinuousDeclineStrategy)
        else:
            c.addstrategy(ContinuousDeclineStrategy, N1=params['N1'],
                          N2=params['N2'],
                          N3=params['N3'],
                          N4=params['N4'])

        return c


class ContinuousDeclineStrategyOptimizer(Optimizer):
    name ="阴跌策略"
    # 策略参数
    params = dict(
        callback=0.02,  # 价格回调比例
        period=100,  # 周期
        down_day=5,  # 连续下跌天数
        stop_loss=0.05,  # 止损比例
        take_profit=0.1,  # 止盈比例
    )
    def get_name(self):
        return self.name
    # 调优参数范围
    optimize_params = dict(
        callback=[0.02, 0.08],  # 价格回调比例
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
        self.params_optimize(
            callback=self.params['callback'],
            down_day=self.params['down_day'],
            period=self.params['period'],
            stop_loss=self.params['stop_loss'],
            take_profit=self.params['take_profit'],
        )
        return self.cerebro.broker.getvalue()

    def params_optimize(self, callback, down_day, period, stop_loss=0.05, take_profit=0.01):
        """
        参数优化
        :param down_day: 连续下跌天数
        :param period: 周期
        :param callback: 价格回撤
        :param stop_loss: 盈亏比 止损
        :param take_profit: 盈亏比 止盈
        """
        self.params = dict(
            callback=callback,  # 价格回调比例
            period=period,  # 周期
            down_day=down_day,  # 连续下跌天数
            stop_loss=stop_loss,  # 止损比例
            take_profit=take_profit,  # 止盈比例
        )
        kines = self.get_data()
        self.cerebro = create_cerebro(self.cash)
        self.cerebro.adddata(kines)
        self.cerebro = add_continuous_decline_strategy(self.cerebro, self.params)

        self.cerebro.run()
        rate = self.cerebro.broker.getvalue() / self.cash
        if rate > 5 or self.is_show_params:
            self.log(f"rate: {rate} ")
            self.log(f"params:{self.params}")
            self.log("")
        return self.cerebro.broker.getvalue()

    def run(self):
        opt = optunity.maximize(
            f=self.params_optimize,
            num_evals=self.event_num,
            solver_name='particle swarm',
            callback=self.optimize_params['callback'],
            down_day=self.optimize_params['down_day'],
            period=self.optimize_params['period'],
            stop_loss=self.optimize_params['stop_loss'],
            take_profit=self.optimize_params['take_profit']
        )
        optimal_pars, details, _ = opt  # optimal_pars 最优参数组合
        self.params = optimal_pars
        return optimal_pars

    def get_optimal_parameters(self):
        """
        获取最优参数
        :return:
        """
        return self.params


def test_op():
    path = "/static/data/ETHUSDT_1h.csv"
    data = load_csv_data(path)
    op = ContinuousDeclineStrategyOptimizer()
    op.set_data(data)
    op.set_event_num(500)
    op.run()
    params = op.get_optimal_parameters()
    cerebro = create_cerebro()
    cerebro.adddata(data)
    add_continuous_decline_strategy(cerebro, params)
    cerebro.addstrategy(ContinuousDeclineStrategy, params)
    cerebro.run()
    cerebro.plot()


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
        app.set_fuc(add_continuous_decline_strategy)
        # app.run()
        opt = ContinuousDeclineStrategyOptimizer()
        # opt.set_data(date)
        opt.set_event_num(500)
        app.set_optimizer(opt)
        # app.run_optimizer()
        app.verify_optimizer(path=file_path)
    # app.add_strategy(strategy=ContinuousDeclineStrategy)
