import asyncio
import logging
import time

import backtrader
import logging as log

from hyperopt import Trials, fmin, tpe

from util import to_json, get_default_strategy_name
import matplotlib.pyplot as plt
import util

from util.ding_talk import send_text_to_dingtalk


def batch_run(strategy, params=None, intervals=None, symbols=None):
    if symbols is None:
        symbols = ['BTC', 'ETH', 'AAVE']
    if intervals is None:
        intervals = ['1d', '5m', '15m', '30m', '1h', '4h']
    loop = asyncio.get_event_loop()

    logging.info(f"started at {time.strftime('%X')}")
    for interval in intervals:
        for symbol in symbols:
            data = util.get_local_generic_csv_data(symbol, interval)
            run(data, strategy, params, is_show=False)
            print(symbol)
            # loop.run_until_complete(async_run(data, strategy, params, is_show=False))

    logging.info(f"finished at {time.strftime('%X')}")


async def async_run(data, strategy, params=None, strategy_name=None, is_show=True, is_log=True):
    """
    运行策略
    :param is_log: 是否记录日志
    :param data: 数据
    :param strategy: 策略
    :param params: 策略参数
    :param is_show: 是否显示图表
    :param strategy_name: 策略名称
    :return:
    """
    run(data, strategy, params, strategy_name, is_show, is_log)


def run(data, strategy, params=None, strategy_name=None, is_show=True, is_log=True):
    """
    运行策略
    :param is_log: 是否记录日志
    :param data: 数据
    :param strategy: 策略
    :param params: 策略参数
    :param is_show: 是否显示图表
    :param strategy_name: 策略名称
    :return:
    """
    if strategy_name is None:
        strategy_name = get_default_strategy_name(strategy, data)
    cerebro = get_default_cerebro()
    cerebro.addstrategy(strategy, params=params)
    cash = cerebro.broker.getcash()
    cerebro.adddata(data)
    cerebro.run()
    if is_log:
        result = {
            "策略": get_default_strategy_name(strategy, data),
            "收益率": f"{(cerebro.broker.getvalue() - cash) / cash * 100} %",
            "参数": params
        }
        log.info(to_json(result))

    if is_show:
        '【蜡烛图样式】'
        plt.style.use('seaborn')  # 使用 seaborn 主题
        plt.rcParams['figure.figsize'] = 20, 10  # 全局修改图大小
        colors = ['#729ece', '#ff9e4a', '#67bf5c', '#ed665d', '#ad8bc9', '#a8786e', '#ed97ca', '#a2a2a2', '#cdcc5d',
                  '#6dccda']
        cerebro.plot(
            # line（收盘价线）颜色
            loc='black',
            # bar/candle上涨线的颜色（灰度：0.75）
            barup='green',
            # bar/candle下跌线的颜色（红色）
            bardown='red',
            # bar/candle的透明度（1表示完全不透明）
            bartrans=1.0,
            # 设置图形之间的间距
            plotdist=0.1,
            # 设置成交量在行情上涨和下跌情况下的颜色
            volup='#ff9896',
            voldown='#98df8a',
            grid=False,  # 删除水平网格
            style='bar',  # 绘制线型价格走势，可改为 'line'  'bar'、'candle' 样式
            lcolors=colors,
        )
    return cerebro
    pass


def get_default_cerebro(cash=10000.0, commission=0.01, stake=100, is_coc=True):
    """
    创建默认的控制器
    :param cash: 初始资金
    :param commission: 佣金率
    :param stake: 交易单位大小
    :param is_coc: 是否开启作弊模式
    :return:
    """
    # 加载backtrader引擎
    cerebro = backtrader.Cerebro()
    # 策略加进来
    cerebro.addsizer(backtrader.sizers.FixedSize, stake=stake)
    # 设置以收盘价成交，作弊模式
    cerebro.broker.set_coc(is_coc)
    # 设置初始金额
    cerebro.broker.set_cash(cash)
    # 设置手续费
    cerebro.broker.setcommission(commission=commission)
    return cerebro


class Actuator:

    def __init__(self, data,
                 strategy,
                 cash=10000,
                 is_send_ding_task=True,
                 strategy_name=None,
                 ):
        self.data = data

        self.is_send_ding_task = is_send_ding_task
        self.params = None
        self.cash = cash,
        self.cash = 10000
        if strategy_name is None:
            strategy_name = get_default_strategy_name(strategy, data)
        self.strategy_name = strategy_name

        self.strategy = strategy

        self.value = 0

    def __target_func(self, params):
        try:
            cerebro = self.run(params=params, is_show=False, is_log=False)
            logging.info(cerebro.broker.getvalue())
            # 记录更加优异的策略参数
            if self.value < cerebro.broker.getvalue():
                self.value = cerebro.broker.getvalue()
                self.params = params
                info = {
                    '优化策略': self.strategy_name,
                    '收益率': f"{(self.value - self.cash) / self.cash * 100} %",
                    '参数': str(self.params),

                }
                logging.info(to_json(info))
            return -cerebro.broker.getvalue()
        except Exception as r:
            logging.info('未知错误 %s' % r)
        return 0

    def run(self, params=None, is_show=True, is_log=True):
        """
        运行策略
        :param is_log: 是否记录日志
        :param params: 策略参数
        :param is_show: 是否显示图表
        :return:
        """

        cerebro = get_default_cerebro(cash=self.cash)
        cerebro.addstrategy(self.strategy, params=params)
        cash = cerebro.broker.getcash()
        cerebro.adddata(self.data)
        cerebro.run()
        if is_log:
            result = {
                "策略": self.strategy_name,
                "收益率": f"{(cerebro.broker.getvalue() - cash) / cash * 100} %",
                "参数": params
            }
            log.info(to_json(result))

        if is_show:
            '【蜡烛图样式】'
            plt.style.use('seaborn')  # 使用 seaborn 主题
            plt.rcParams['figure.figsize'] = 20, 10  # 全局修改图大小
            colors = ['#729ece', '#ff9e4a', '#67bf5c', '#ed665d', '#ad8bc9', '#a8786e', '#ed97ca', '#a2a2a2', '#cdcc5d',
                      '#6dccda']
            cerebro.plot(
                # line（收盘价线）颜色
                loc='black',
                # bar/candle上涨线的颜色（灰度：0.75）
                barup='green',
                # bar/candle下跌线的颜色（红色）
                bardown='red',
                # bar/candle的透明度（1表示完全不透明）
                bartrans=1.0,
                # 设置图形之间的间距
                plotdist=0.1,
                # 设置成交量在行情上涨和下跌情况下的颜色
                volup='#ff9896',
                voldown='#98df8a',
                grid=False,  # 删除水平网格
                style='bar',  # 绘制线型价格走势，可改为 'line'  'bar'、'candle' 样式
                lcolors=colors,
            )
        return cerebro

    def opt(self, space, max_evals=200):
        trials = Trials()
        self.params = fmin(fn=self.__target_func, space=space, algo=tpe.suggest, max_evals=max_evals,
                           trials=trials)

        if self.is_send_ding_task:
            info = {
                '优化策略': self.strategy_name,
                "收益率": f"{(self.value - self.cash) / self.cash * 100} %",
                '参数': str(self.params),

            }
            send_text_to_dingtalk(to_json(info))
        logging.info(f' {to_json(info)}')
        return self.params

    def opt_plot(self):
        self.run(params=self.params, is_show=True)
