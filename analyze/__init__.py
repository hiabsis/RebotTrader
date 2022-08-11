import setting
import backtrader
import pandas
import pyfolio
import matplotlib.ticker as ticker
import matplotlib.pyplot as plt

# -*- coding: UTF-8 -*-
import strategy
import datetime
import logging
import time
import asyncio
import backtrader as bt
import quantstats
import webbrowser
import setting
import backtrader
import pandas
import pyfolio
import matplotlib.ticker as ticker
import matplotlib.pyplot as plt
from backtrader_plotting import Bokeh
from backtrader_plotting.schemes import Tradimo
from setting import save_analyze_path
from utils import send_text_to_dingtalk, to_json, generate_random_str, \
    timestamp2str
from util import file_util


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
    strategy.run_strategy(create_strategy_func=func, data=data, params=params, is_show=is_show)
    print("async_async_run_strategy\n")


async def async_analyze_strategy_task(data, func, params=None, is_show=True):
    """
    异步策略分析发任务
    :param data:
    :param func:
    :param params:
    :param is_show:
    :return:
    """
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


def show_strategy_analyze(data, func, params=None, is_show=False):
    asyncio.run(async_analyze_strategy_task(data, func, params, is_show))


def simple_analyze(func, data, params=None, name="DEFAULT_NAME"):
    cerebro = func(params)
    cerebro.adddata(data)
    # 回测时需要添加 TimeReturn 分析器
    cerebro.addanalyzer(backtrader.analyzers.TimeReturn, _name='_TimeReturn')
    result = cerebro.run()

    # 提取收益序列
    pnl = pandas.Series(result[0].analyzers._TimeReturn.get_analysis())
    # 计算累计收益
    cumulative = (pnl + 1).cumprod()
    # 计算回撤序列
    max_return = cumulative.cummax()
    drawdown = (cumulative - max_return) / max_return
    # 按年统计收益指标
    perf_stats_year = pnl.groupby(pnl.index.to_period('y')).apply(
        lambda data: pyfolio.timeseries.perf_stats(data)).unstack()
    # 统计所有时间段的收益指标
    perf_stats_all = pyfolio.timeseries.perf_stats(pnl).to_frame(name='all')
    perf_stats = pandas.concat([perf_stats_year, perf_stats_all.T], axis=0)
    perf_stats_ = round(perf_stats, 4).reset_index()
    # 支持中文
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
    plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

    # plt.style.use('seaborn')
    plt.style.use('dark_background')

    fig, (ax0, ax1) = plt.subplots(2, 1, gridspec_kw={'height_ratios': [1.5, 4]}, figsize=(20, 8))
    cols_names = ['date\n', 'Annual\nreturn', 'Cumulative\nreturns', 'Annual\nvolatility',
                  'Sharpe\nratio', 'Calmar\nratio', 'Stability\n', 'Max\ndrawdown',
                  'Omega\nratio', 'Sortino\nratio', 'Skew\n', 'Kurtosis\n', 'Tail\nratio',
                  'Daily value\nat risk']

    # 绘制表格
    ax0.set_axis_off()  # 除去坐标轴
    table = ax0.table(cellText=perf_stats_.values,
                      bbox=(0, 0, 1, 1),  # 设置表格位置， (x0, y0, width, height)
                      rowLoc='right',  # 行标题居中
                      cellLoc='right',
                      colLabels=cols_names,  # 设置列标题
                      colLoc='right',  # 列标题居中
                      edges='open'  # 不显示表格边框
                      )
    table.set_fontsize(13)

    # 绘制累计收益曲线
    ax2 = ax1.twinx()
    ax1.yaxis.set_ticks_position('right')  # 将回撤曲线的 y 轴移至右侧
    ax2.yaxis.set_ticks_position('left')  # 将累计收益曲线的 y 轴移至左侧
    # 绘制回撤曲线
    drawdown.plot.area(ax=ax1, label='drawdown (right)', rot=0, alpha=0.3, fontsize=13, grid=False)
    # 绘制累计收益曲线
    cumulative.plot(ax=ax2, color='#F1C40F', lw=3.0, label='cumret (left)', rot=0, fontsize=13, grid=False)
    # 不然 x 轴留有空白
    ax2.set_xbound(lower=cumulative.index.min(), upper=cumulative.index.max())
    # 主轴定位器：每 5 个月显示一个日期：根据具体天数来做排版
    ax2.xaxis.set_major_locator(ticker.MultipleLocator(100))
    # 同时绘制双轴的图例
    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    plt.legend(h1 + h2, l1 + l2, fontsize=12, loc='upper left', ncol=1)
    save_path = setting.save_analyze_path + "\\" + "simple_analyze_" + name + ".jpg"
    fig.tight_layout()  # 规整排版
    plt.show()


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


def simple_analyze_polt(create_strategy_fun, data, params=None, name="DEFAULT_NAME"):
    """
    显示简单的回测信息
    :param create_strategy_fun:

    :param data:
    :param params:
    :param name:
    :return:
    """
    cerebro = create_strategy_fun(params)
    cerebro.adddata(data)
    # 回测时需要添加 TimeReturn 分析器
    cerebro.addanalyzer(backtrader.analyzers.TimeReturn, _name='_TimeReturn')
    result = cerebro.run()

    # 提取收益序列
    pnl = pandas.Series(result[0].analyzers._TimeReturn.get_analysis())
    # 计算累计收益
    cumulative = (pnl + 1).cumprod()
    # 计算回撤序列
    max_return = cumulative.cummax()
    drawdown = (cumulative - max_return) / max_return
    # 按年统计收益指标
    perf_stats_year = pnl.groupby(pnl.index.to_period('y')).apply(
        lambda data: pyfolio.timeseries.perf_stats(data)).unstack()
    # 统计所有时间段的收益指标
    perf_stats_all = pyfolio.timeseries.perf_stats(pnl).to_frame(name='all')
    perf_stats = pandas.concat([perf_stats_year, perf_stats_all.T], axis=0)
    perf_stats_ = round(perf_stats, 4).reset_index()
    # 支持中文
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
    plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

    # plt.style.use('seaborn')
    plt.style.use('dark_background')

    fig, (ax0, ax1) = plt.subplots(2, 1, gridspec_kw={'height_ratios': [1.5, 4]}, figsize=(20, 8))
    cols_names = ['date\n', 'Annual\nreturn', 'Cumulative\nreturns', 'Annual\nvolatility',
                  'Sharpe\nratio', 'Calmar\nratio', 'Stability\n', 'Max\ndrawdown',
                  'Omega\nratio', 'Sortino\nratio', 'Skew\n', 'Kurtosis\n', 'Tail\nratio',
                  'Daily value\nat risk']

    # 绘制表格
    ax0.set_axis_off()  # 除去坐标轴
    table = ax0.table(cellText=perf_stats_.values,
                      bbox=(0, 0, 1, 1),  # 设置表格位置， (x0, y0, width, height)
                      rowLoc='right',  # 行标题居中
                      cellLoc='right',
                      colLabels=cols_names,  # 设置列标题
                      colLoc='right',  # 列标题居中
                      edges='open'  # 不显示表格边框
                      )
    table.set_fontsize(13)

    # 绘制累计收益曲线
    ax2 = ax1.twinx()
    ax1.yaxis.set_ticks_position('right')  # 将回撤曲线的 y 轴移至右侧
    ax2.yaxis.set_ticks_position('left')  # 将累计收益曲线的 y 轴移至左侧
    # 绘制回撤曲线
    drawdown.plot.area(ax=ax1, label='drawdown (right)', rot=0, alpha=0.3, fontsize=13, grid=False)
    # 绘制累计收益曲线
    cumulative.plot(ax=ax2, color='#F1C40F', lw=3.0, label='cumret (left)', rot=0, fontsize=13, grid=False)
    # 不然 x 轴留有空白
    ax2.set_xbound(lower=cumulative.index.min(), upper=cumulative.index.max())
    # 主轴定位器：每 5 个月显示一个日期：根据具体天数来做排版
    ax2.xaxis.set_major_locator(ticker.MultipleLocator(100))
    # 同时绘制双轴的图例
    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    plt.legend(h1 + h2, l1 + l2, fontsize=12, loc='upper left', ncol=1)
    save_path = setting.save_analyze_path + "\\" + "simple_analyze_" + name + ".jpg"
    # plt.savefig(save_path)
    fig.tight_layout()  # 规整排版
    plt.show()
    # plt.savefig(save_path)
