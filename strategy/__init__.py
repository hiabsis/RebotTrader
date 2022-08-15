# -*- coding: UTF-8 -*-

import datetime
import logging
import os
from hyperopt import fmin, tpe, Trials, hp
import backtrader as bt
import logging as log
import numpy
import setting
import pandas

from utils import load_csv_data, send_text_to_dingtalk, to_json, save_to_text, add_mouth


def create_strategy(strategy, p=None):
    c = create_cerebro()
    if p:
        c.addstrategy(strategy=strategy, params=p)
    else:
        c.addstrategy(strategy)
    return c


def create_cerebro(cash=10000.0, commission=0.01, stake=100):
    """
    :param cash: 初始资金
    :param commission: 佣金率
    :param stake: 交易单位大小
    :param strategy: 交易策略
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


def optimize_strategy(func, space, max_evals=400):
    """
    参数优化
    :param func: 目标函数
    :param space: 参数搜索空间     {'x': hp.uniform('x', -5, 5) }
    :param max_evals: 迭代次数
    :return:
    """
    trials = Trials()
    return fmin(fn=func, space=space, algo=tpe.suggest, max_evals=max_evals, trials=trials)


def run(data, strategy, params=None, is_show=False, is_log=False, is_update_params=False, cash=10000, stake=10,
        commission=0.01, name=''):
    """
    运行策略
    :param stake:
    :param cash:
    :param commission:
    :param cash:
    :param is_update_params:
    :param is_log:
    :param data: 数据
    :param strategy: 策略
    :param params: 策略参数
    :param is_show: 是否显示图表
    :param name: 策略名称
    :return:
    """
    cerebro = create_strategy(strategy, params)
    cash = cerebro.broker.getcash()
    cerebro.adddata(data)
    cerebro.run()
    if is_log:
        result = {
            "策略名称": name,
            "数据源": data._dataname,
            "收益率": f"{(cerebro.broker.getvalue() - cash) / cash * 100} %",
            "参数": params
        }
    if is_show:
        cerebro.plot()
    log.info(result)


def run_strategy(data, create_strategy_func=None, params=None, cash=10000, is_show=False,
                 ):
    """
    运行策略
    :param strategy:
    :param create_strategy_func: 添加策略函数
    fun (cerebro:Cerebro,params):
        return cerebro
    :param params: 策略参数
    :param data: 数据
    :param cash: 初始资金
    :param is_show:  是否显示回测结果
    :return: cerebro
    """
    if create_strategy_func is None:
        create_strategy_func = create_strategy
    cerebro = create_strategy_func(params)
    cerebro.adddata(data)
    cerebro.run()
    if is_show:
        info = {
            "策略名称": "",
            "数据源": data._dataname,
            "收益率": f"{(cerebro.broker.getvalue() - cash) / cash * 100} %",
            "参数": params
        }
        log.info(to_json(info))
        cerebro.plot()

    return cerebro


def get_data(path):
    data = load_csv_data(path)
    return data


class Optimizer:

    def __init__(self, data, space, create_strategy_func, max_evals=500, is_send_ding_task=True, strategy_name=''):
        self.data = data
        self.max_evals = max_evals
        self.is_send_ding_task = is_send_ding_task
        self.params = None
        self.cash = 10000
        self.space = space
        self.strategy_name = strategy_name
        self.create_strategy_func = create_strategy_func
        self.value = 0

    def target_func(self, params):
        try:

            cerebro = run_strategy(create_strategy_func=self.create_strategy_func, data=self.data,
                                   cash=self.cash, params=params)
            # 记录更加优异的策略参数
            if self.value < cerebro.broker.getvalue():
                self.value = cerebro.broker.getvalue()
                self.params = params
                info = {
                    '优化策略': self.strategy_name,
                    '收益率': f"{(self.value - self.cash) / self.cash * 100} %",
                    '参数': str(self.params),

                }
                print(info)
            return -cerebro.broker.getvalue()
        except Exception as r:
            logging.error('未知错误 %s' % r)
        return 0

    def run(self):
        trials = Trials()
        self.params = fmin(fn=self.target_func, space=self.space, algo=tpe.suggest, max_evals=self.max_evals,
                           trials=trials)
        logging.info(f'最优参数 {self.params}')
        if self.is_send_ding_task:
            info = {
                '优化策略': self.strategy_name,
                '收益率': f"{(self.value - self.cash) / self.cash * 100} %",
                '参数': str(self.params),

            }
            send_text_to_dingtalk(to_json(info))
        return self.params

    def plot(self):
        run_strategy(create_strategy_func=self.create_strategy_func, data=self.data, params=self.params, is_show=True)


def batch_optimizer(strategy_func, space, root=None, strategy_name="batch_optimizer",
                    max_evals=500,
                    is_send_ding_talk=False):
    if root is None:
        root = setting.date_root_path
    file_name = os.listdir(path=root)
    save_params = []
    message = []
    for i in file_name:
        path = root + "\\" + i
        start = datetime.datetime.now().timestamp()
        data = get_data(path)
        cash = 100000

        opt = Optimizer(data=data, space=space, max_evals=max_evals, create_strategy_func=strategy_func)
        params = opt.run()
        end = datetime.datetime.now().timestamp()
        execute_time = (end - start) / 60
        try:
            cerebro = run_strategy(create_strategy_func=strategy_func, data=data, params=params, cash=cash)
            info = {
                "策略名称": strategy_name,
                "运行时间": f"{execute_time}分钟",
                "数据源": path,
                "收益率": f"{cerebro.broker.getvalue() / cash * 100} %",
                "参数": str(params)
            }
            print(to_json(info))
            save_params.append(params)
            message.append(info)
        except Exception as r:
            print('未知错误 %s' % r)
    if is_send_ding_talk:
        send_text_to_dingtalk(to_json(message))
    save_path = "D:\\work\\git\\Tools\\static\\params\\" + strategy_name + ".txt"
    save_to_text(to_json(save_path), path=save_path)


def performance_optimizer(create_strategy_func, space, path, period=12,
                          strategy_name='', cash=10000, is_notify=False):
    """
    :param create_strategy_func: 添加策略函数
    :param space: 参数空间
    :param path: 数据路径
    :param period: 周期
    :param strategy_name: 策略名称
    :param cash:
    :param is_notify:
    :return:
    """
    data = pandas.read_csv(path)
    data = numpy.array(data)
    start_time = datetime.datetime.strptime(data[0][0], "%Y-%m-%d %H:%M:%S")
    stop_time = datetime.datetime.strptime(data[len(data) - 1][0], "%Y-%m-%d %H:%M:%S")
    end_time = add_mouth(start_time, period)
    data = load_csv_data(path, start_time, end_time)
    opt = Optimizer(data=data, space=space, create_strategy_func=create_strategy_func)
    params = opt.run()
    message = {
        'task': "performance_optimizer",
        'strategy': strategy_name,
        'start_time': datetime.datetime.now(),
        'performance': [],

    }

    while True:

        start_time = add_mouth(start_time, period)

        end_time = add_mouth(end_time, period)
        is_end = start_time.timestamp() >= stop_time.timestamp()
        if is_end:
            break
        # 运行策略
        data = load_csv_data(path, start_time, end_time)
        cerebro = run_strategy(create_strategy_func=create_strategy_func, data=data, cash=cash, params=params)
        value = cerebro.broker.getvalue()
        info = dict(
            path=path,
            time=f"{start_time}  {end_time}",
            cash=cash,
            value=value,
            sharpe_ratio=value / cash,
            params=params,
        )
        message['performance'].append(info)

        cash = value
        opt = Optimizer(data=data, space=space, create_strategy_func=create_strategy_func)
        params = opt.run()

        print(message)

        if is_notify:
            send_text_to_dingtalk(to_json(message))
    return message


def batch_performance_optimizer(strategy_func, space, root="D:\\work\\git\\Tools\\static\\data",
                                strategy_name="strategy",
                                is_notify=False):
    file_names = os.listdir(path=root)
    save_params = []
    for file in file_names:
        path = root + "\\" + file
        params = performance_optimizer(strategy_name=strategy_name, create_strategy_func=strategy_func, path=path,
                                       space=space,
                                       is_notify=True)
        save_params.append(params)

    save_path = "D:\\work\\git\\Tools\\static\\params" + "\\" + strategy_name + ".text"
    save_to_text(to_json(save_params), save_path)


