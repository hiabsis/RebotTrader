import datetime
import logging
import os
import time
import asyncio
from hyperopt import fmin, tpe, Trials, hp
import backtrader as bt
import logging as log
import numpy
import pandas
import quantstats
import webbrowser
import setting
from backtrader_plotting import Bokeh
from backtrader_plotting.schemes import Tradimo
from setting import save_analyze_path
from utils import load_csv_data, send_text_to_dingtalk, to_json, save_to_text, add_mouth, generate_random_str, \
    timestamp2str
from util import file_util, data_util


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


def run_strategy(create_strategy_func, data, params=None, cash=10000, is_show=False):
    """
    运行策略
    :param create_strategy_func: 添加策略函数
    fun (cerebro:Cerebro,params):
        return cerebro
    :param params: 策略参数
    :param data: 数据
    :param cash: 初始资金
    :param is_show:  是否显示回测结果
    :return: cerebro
    """
    cerebro = create_strategy_func(params)
    cerebro.adddata(data)
    cerebro.run()
    if is_show:
        info = {
            "策略名称": get_strategy_name(func=create_strategy_func, file=data._dataname),
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

    def __init__(self, data, space, create_strategy_func, max_evals=500, is_send_ding_task=False):
        self.data = data
        self.max_evals = max_evals
        self.is_send_ding_task = is_send_ding_task
        self.params = None
        self.cash = 10000
        self.space = space
        self.create_strategy_func = create_strategy_func

    def target_func(self, params):
        cerebro = run_strategy(create_strategy_func=self.create_strategy_func, data=self.data,
                               cash=self.cash, params=params)
        return -cerebro.broker.getvalue()

    def run(self):
        trials = Trials()
        self.params = fmin(fn=self.target_func, space=self.space, algo=tpe.suggest, max_evals=self.max_evals,
                           trials=trials)
        logging.info(self.params)
        if self.is_send_ding_task:
            info = {
                '参数优化器': "",
                '优化策略': str(self.create_strategy_func),
                '参数': self.params,

            }
            send_text_to_dingtalk(to_json(info))
        return self.params

    def plot(self):
        run_strategy(create_strategy_func=self.create_strategy_func, data=self.data, params=self.params, is_show=True)


def batch_optimizer(strategy_func, space, root=None, name=None,
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

        opt = Optimizer(data=data, space=space, create_strategy_func=strategy_func)
        params = opt.run()
        end = datetime.datetime.now().timestamp()
        execute_time = (end - start) / 60
        cerebro = run_strategy(create_strategy_func=strategy_func, data=data, params=params, cash=cash)
        info = {
            "策略名称": name,
            "运行时间": f"{execute_time}分钟",
            "数据源": path,
            "收益率": f"{cerebro.broker.getvalue() / cash * 100} %",
            "参数": params
        }
        print(to_json(info))
        save_params.append(params)
        message.append(info)
    if is_send_ding_talk:
        send_text_to_dingtalk(to_json(message))
    save_path = "D:\\work\\git\\Tools\\static\\params\\" + name + ".txt"
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


def show_strategy_pyfolio(data, create_strategy_func, params=None, file_name="pyfolio", title='Returns Sentiment',
                          is_show=False):
    """
    可视化分析 财务数据
    :param params:
    :param create_strategy_func:
    :param data:
    :param file_name:
    :param title:
    :param is_show:
    :return:
    """
    cerebro = create_strategy_func(params)
    cerebro.adddata(data)
    cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')
    back = cerebro.run()
    portfolio = back[0].analyzers.getbyname('pyfolio')
    returns, positions, transactions, gross_lev = portfolio.get_pf_items()
    returns.index = returns.index.tz_convert(None)
    file_name = get_strategy_name(func=create_strategy_func, file=data._dataname)
    pyfolio_output = save_analyze_path + "\\pyfolio_" + file_name + ".html"
    quantstats.reports.html(returns, output=pyfolio_output, download_filename=pyfolio_output, title=title)
    if is_show:
        webbrowser.open(pyfolio_output)
    path = file_util.html2img(pyfolio_output)
    path = file_util.compress_image(path)
    return path


def show_strategy_analyze(data, create_strategy_func, params=None,
                          is_show=False):
    """
     可视化分析
    :param data:
    :param create_strategy_func:
    :param params:
    :param is_show:
    :return:
    """
    cerebro = create_strategy_func(params)
    cerebro.adddata(data)
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='SharpeRatio')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='DW')
    cerebro.addanalyzer(bt.analyzers.AnnualReturn, _name='AnnualReturn')
    cerebro.addanalyzer(bt.analyzers.Returns, _name='Returns')
    cerebro.addanalyzer(bt.analyzers.SQN, _name='SQN')
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer)
    # 添加观测器observers
    cerebro.addobserver(bt.observers.Broker)
    cerebro.addobserver(bt.observers.Trades)
    cerebro.addobserver(bt.observers.BuySell)
    cerebro.addobserver(bt.observers.DrawDown)
    cerebro.addobserver(bt.observers.Benchmark)
    cerebro.addobserver(bt.observers.TimeReturn)
    cerebro.addobserver(bt.observers.Value)
    cerebro.run()
    file_name = get_strategy_name(func=create_strategy_func, file=data._dataname)
    bokeh_output = save_analyze_path + "\\bokeh_" + file_name + ".html"
    if is_show:
        b = Bokeh(style='bar', scheme=Tradimo(), filename=bokeh_output, output_mode="show")  # 传统白底，多页

    else:
        b = Bokeh(style='bar', scheme=Tradimo(), filename=bokeh_output, output_mode="save")  # 传统白底，多页
    cerebro.plot(b)
    # 转图片存在bug暂时不转换
    # path = file_util.html2img(bokeh_output)
    # path = file_util.compress_image(path)
    return bokeh_output


def get_strategy_name(func, file=""):
    strategy_name = str(func).split(" ")[1]
    data_info = file.split('\\')[-1].split('.')[0]
    strategy_name = strategy_name + "_" + data_info + "_" \
                    + timestamp2str(int(datetime.datetime.now().timestamp()), format="%Y_%m_%d_%H_%M") + "_" \
                    + generate_random_str(12)
    return strategy_name


async def async_show_analyze(data, func, params=None, is_show=False):
    path = show_strategy_analyze(data,
                                 params=params,
                                 create_strategy_func=func,
                                 is_show=is_show)
    info = {
        "策略名称": str(func),
        "类型": "analyzer",
        "数据源": data._dataname,
        "分析结果": path
    }
    logging.info(f"async_show_analyze\n {to_json(info)}")
    send_text_to_dingtalk(to_json(info))
    return


async def async_show_pyfolio(data, func, params=None, is_show=False):
    path = show_strategy_analyze(data,
                                 params=params,
                                 create_strategy_func=func,
                                 is_show=is_show)
    info = {
        "策略名称": str(func),
        "类型": "pyfolio",
        "数据源": data._dataname,
        "分析结果": path
    }
    logging.info(f"async_show_pyfolio\n {to_json(info)}")
    send_text_to_dingtalk(to_json(info))


async def async_run_strategy(data, func, params=None, is_show=False):
    run_strategy(create_strategy_func=func, data=data, params=params, is_show=is_show)
    print("async_async_run_strategy\n")


async def async_test_strategy(data, func, params=None, is_show=True):
    message = {}
    task1 = asyncio.create_task(
        async_show_analyze(data, func, params, is_show)
    )

    task2 = asyncio.create_task(
        async_run_strategy(data, func, params, is_show)
    )
    task3 = asyncio.create_task(
        async_show_pyfolio(data, func, params, is_show)
    )
    print(f"started at {time.strftime('%X')}")

    # Wait until both tasks are completed (should take around 2 seconds.)
    # 两个任务同时执行，直到到所有任务执行完成。
    await task1
    await task2
    await task3
    print(f"finished at {time.strftime('%X')}")


def show_strategy(data, func, params=None, is_show=False):
    asyncio.run(async_test_strategy(data, func, params, is_show))
