import math

import backtrader
from hyperopt import hp

import actuator
import setting
import util.data_util as data_util
from util import to_json, file_util
import strategy


def get_order_info(order):
    order_status = ['Created', 'Submitted', 'Accepted', 'Partial',
                    'Completed', 'Canceled', 'Expired', 'Margin', 'Rejected']
    return to_json(
        dict(
            EXECUTED_STATUS=order_status[order.status],
            ID=order.ref,
            NAME=order_status[order.status],
            SIZE=order.executed.size,
            PRICE=order.executed.price,
            VALUE=order.executed.value,
            COMM=order.executed.comm,

        )
    )


class MartinStrategy(backtrader.Strategy):
    """
    马丁策略
    每跌2%加2倍仓位 加9次仓
    盈利2%跑路
    """
    params = dict(
        # 多加仓次数
        max_buy_number=10,
        # 买入价格后每跌2%加仓
        down_proportion=0.05,
        # 每次盈利2%出场
        sell_proportion=0.05,
        # sma周期
        period=200,
        #  是否记录日志
        printlog=True
    )

    def __init__(self, params=None):
        # 处理参数
        if params:
            if 'max_buy_number' in params:
                self.p.max_buy_number = params['max_buy_number']
            if 'down_proportion' in params:
                self.p.down_proportion = params['down_proportion']
            if 'sell_proportion' in params:
                self.p.sell_proportion = params['sell_proportion']
            if 'period' in params:
                self.p.period = params['period']
        # 首次下单时,订单价格
        self.buy_price = 0
        # 下单后，持仓价值
        self.buy_value = 0
        # 首次下单时，持有现金
        self.buy_cash = 0
        # 加仓次数
        self.buy_frequency = 0
        # 下单后总持有量
        self.buy_size = 0
        # 总仓位
        self.total_size = 0
        # 总仓位尺寸
        for i in range(self.p.max_buy_number - 1):
            self.total_size = self.total_size + math.pow(2, i)
        # 订单情况
        self.order = None
        self.sma = backtrader.ind.SMA(period=self.p.period)

    def to_buy(self):
        if self.buy_frequency > self.p.max_buy_number:
            return
        if self.buy_frequency == 0:
            # 首次下单时,持有现金
            self.buy_cash = self.broker.getcash()
            # 首次下单时,订单价格
            self.buy_price = self.data.close[0]

        # 仓位比例
        position = math.pow(2, self.buy_frequency) / self.total_size
        # 买入的资金
        buy_cash = position * self.buy_cash
        # 买入数量
        size = buy_cash / self.buy_price

        self.buy_size = size + self.buy_size
        # 加仓
        self.buy_frequency = self.buy_frequency + 1
        # 下单后，持仓价值
        self.buy_value = self.buy_value + buy_cash
        # 买入
        self.order = self.buy(size=size, price=data.close[0])

    def log(self, txt, dt=None):
        if self.params.printlog:
            dt = dt or self.datas[0].datetime.date(0)
            print(f'{dt.isoformat()},{txt}')

    def notify_order(self, order):

        # 未被处理的订单
        if order.status in [order.Submitted, order.Accepted]:
            return
        # 已经处理的订单
        if order.status in [order.Partial, order.Completed]:
            if order.isbuy():
                pass

            else:  # Sell
                self.buy_frequency = 0
                self.buy_cash = 0
                self.buy_price = 0
                self.buy_value = 0
                self.buy_size = 0

        self.order = None

    def next(self):
        if self.order:
            self.log(get_order_info(self.order))
            return
        # 没有仓位
        if not self.position:
            # 收盘价高于价格sma
            if self.data.close[0] > self.sma[-1]:
                self.to_buy()
                return
        if self.position:
            # 计算持仓成本
            buy_price = self.buy_value / self.buy_size

            if (self.data.close[0] - buy_price) / buy_price > self.p.sell_proportion:
                # 盈利2%平仓
                self.close()
                return
            if (self.data.close[0] - self.buy_price) / self.buy_price < - self.p.down_proportion * self.buy_frequency:
                # 每跌2%加仓
                self.to_buy()
                return


class MartinV1Strategy(backtrader.Strategy):
    """
    马丁策略
    每跌2%加2倍仓位 加9次仓
    盈利2%跑路
    加入错空策略
    """
    params = dict(
        # 多加仓次数
        max_buy_number=10,
        # 买入价格后每跌2%加仓
        down_proportion=0.05,
        # 每次盈利2%出场
        sell_proportion=0.05,
        # sma周期
        period=200,
        #  是否记录日志
        printlog=True
    )

    def __init__(self, params=None):
        # 处理参数
        if params:
            if 'max_buy_number' in params:
                self.p.max_buy_number = params['max_buy_number']
            if 'down_proportion' in params:
                self.p.down_proportion = params['down_proportion']
            if 'sell_proportion' in params:
                self.p.sell_proportion = params['sell_proportion']
            if 'period' in params:
                self.p.period = params['period']
        # 首次下单时,订单价格
        self.buy_price = 0
        # 下单后，持仓价值
        self.buy_value = 0
        # 首次下单时，持有现金
        self.buy_cash = 0
        # 加仓次数
        self.buy_frequency = 0
        # 下单后总持有量
        self.buy_size = 0
        # 总仓位
        self.total_size = 0
        # 总仓位尺寸
        for i in range(self.p.max_buy_number - 1):
            self.total_size = self.total_size + math.pow(2, i)
        # 订单情况
        self.order = None
        self.sma = backtrader.ind.SMA(period=self.p.period)

    def to_buy(self, buy_type=1):
        """
        下单
        :param buy_type:  1 买入 2 卖出
        :return:
        """
        if self.buy_frequency > self.p.max_buy_number:
            return
        if self.buy_frequency == 0:
            # 首次下单时,持有现金
            self.buy_cash = self.broker.getcash()
            # 首次下单时,订单价格
            self.buy_price = self.data.close[0]

        # 仓位比例
        position = math.pow(2, self.buy_frequency) / self.total_size
        # 买入的资金
        buy_cash = position * self.buy_cash
        # 买入数量
        size = buy_cash / self.buy_price

        self.buy_size = size + self.buy_size
        # 加仓
        self.buy_frequency = self.buy_frequency + 1
        # 下单后，持仓价值
        self.buy_value = self.buy_value + buy_cash
        if buy_type:
            # 买入
            self.order = self.buy(size=size, price=data.close[0])
        else:
            # 买入
            self.order = self.sell(size=size, price=data.high[0])

    def log(self, txt, dt=None):
        if self.params.printlog:
            dt = dt or self.datas[0].datetime.date(0)
            print(f'{dt.isoformat()},{txt}')

    def notify_order(self, order):

        # 未被处理的订单
        if order.status in [order.Submitted, order.Accepted]:
            return
        # 已经处理的订单
        if order.status in [order.Partial, order.Completed]:
            if order.isbuy():
                pass

            else:  # Sell
                pass

        self.order = None

    def next(self):
        if self.order:
            self.log(get_order_info(self.order))
            return
        # 没有仓位
        if not self.position:
            # # 收盘价高于价格sma
            if self.data.close[0] > self.sma[-1]:
                self.to_buy(buy_type=1)
                return
            if self.data.close[0] < self.sma[-1]:
                self.to_buy(buy_type=-1)
                return
        if self.position.size > 0:
            print("buy")
            # 计算持仓成本
            buy_price = self.buy_value / self.buy_size
            # 平仓
            if (self.data.close[0] - buy_price) / buy_price > self.p.sell_proportion:
                # 盈利2%平仓
                self.close()
                self.buy_frequency = 0
                self.buy_cash = 0
                self.buy_price = 0
                self.buy_value = 0
                self.buy_size = 0
                return
            if (self.data.close[0] - self.buy_price) / self.buy_price < - self.p.down_proportion * self.buy_frequency:
                # 每跌2%加仓
                self.to_buy(buy_type=1)
                return
        if self.position.size < 0:
            print("sell")
            # 计算持仓成本
            buy_price = self.buy_value / self.buy_size

            if (buy_price - self.data.close[0]) / buy_price > self.p.sell_proportion:
                # 盈利2%平仓
                self.close()
                self.buy_frequency = 0
                self.buy_cash = 0
                self.buy_price = 0
                self.buy_value = 0
                self.buy_size = 0
                return
            if (self.buy_price - self.data.close[0]) / self.buy_price < - self.p.down_proportion * self.buy_frequency:
                # 每跌2%加仓
                self.to_buy(buy_type=-1)
                return


def create_martin_v0(params=None):
    c = actuator.create_default_cerebro()
    c.addstrategy(MartinStrategy, params=params)
    return c


def create_martin_v1(params=None):
    c = actuator.create_default_cerebro()
    c.addstrategy(MartinV1Strategy, params=params)
    return c


if __name__ == '__main__':

    func = create_martin_v0()
    s = MartinStrategy
    # 运行策略
    # data = data_util.get_local_generic_csv_data('ETH', '1h')
    # actuator.run(data, s, 'MartinStrategy_ETH_1h')
    params = None
    params_list = []
    # 参数优化
    space = dict(
        # 多加仓次数
        max_buy_number=hp.randint('max_buy_number', 10),
        # 买入价格后每跌2%加仓
        down_proportion=hp.uniform('down_proportion', 0, 0.1),
        # 每次盈利2%出场
        sell_proportion=hp.uniform('sell_proportion', 0, 0.1),
        period=hp.randint('period', 20, 400),
    )
    # param = strategy.Optimizer(data, space, create_martin, max_evals=500, strategy_name='MartinStrategy_ETH_5m').run()
    # 显示优化后的结果
    # actuator.run(data, MartinStrategy, 'MartinStrategy_ETH_5m', param)

    # 不同时间级别情况下的收益
    symbols = ['ETH', 'OP', 'ENS', 'BTC', 'APE', 'KNC', 'GMT', 'BNB', 'DOT']
    intervals = ['1h', '30m', '15m', '5m']

    for interval in intervals:
        for symbol in symbols:
            data_util.down_load_data(symbol, interval)
            data = data_util.get_local_generic_csv_data(symbol, interval)
            param = strategy.Optimizer(data, space, func, max_evals=500,
                                       strategy_name=f'MartinStrategy{symbol}_{interval}').run()
            params_list.append({
                "策略": f'MartinStrategy{symbol}_{interval}',
                "params": to_json(param)
            })
    output = 'D:\\work\\git\\RebotTrader' + "\\static\\params\\" + f'MartinStrategy' + ".json"
    file_util.save_json(output, params_list)
