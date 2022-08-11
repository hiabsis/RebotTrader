import asyncio

import backtrader
import logging as log

import actuator
from strategy.good.art import AtrStrategy
from util import to_json, data_util

loop = asyncio.get_event_loop()


def run(data, strategy, strategy_name, params=None, is_show=True, is_log=True):
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
    cerebro = create_default_cerebro()
    cerebro.addstrategy(strategy, params=params)
    cash = cerebro.broker.getcash()
    cerebro.adddata(data)
    cerebro.run()
    if is_log:
        result = get_back_results_info(strategy_name, data, cerebro, cash, params)
        log.info(to_json(result))
    if is_show:
        cerebro.plot()
    pass


def get_back_results_info(strategy_name, data, cerebro, init_cash, params):
    """
    获取回测信息
    :param params: 策略参数
    :param strategy_name:  策略名称
    :param data: 数据
    :param cerebro: 控制器
    :param init_cash: 初始资金
    :return:
    """
    result = {
        "策略名称": strategy_name,
        "数据源": str(data._dataname).split("\\")[-1].split('.')[0],
        "收益率": f"{(cerebro.broker.getvalue() - init_cash) / init_cash * 100} %",
        "参数": params
    }
    return result


def create_strategy(strategy, p=None, c=None):
    if c is None:
        c = create_default_cerebro()
    if p:
        c.addstrategy(strategy=strategy, params=p)
    else:
        c.addstrategy(strategy)
    return c


def plt():
    pass


def create_default_cerebro(cash=10000.0, commission=0.01, stake=100, is_coc=True):
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



