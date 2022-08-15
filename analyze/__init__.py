import datetime
import logging
import os
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
from util import file_util, data_util, get_default_strategy_name
import actuator
from strategy.good import art


def simple_analyze_plot(data, s, params=None, is_show=False, output=None):
    """
    财务分析
    :return:
    """
    pass


def pyfolio_analyze_plot(data, strategy, params=None, title='Returns Sentiment', output=None,
                         is_show=True):
    """
    可视化分析 财务数据
    :param output:
    :param params:
    :param strategy:
    :param data:
    :param title:
    :param is_show:
    :return:
    """
    cerebro = actuator.get_default_cerebro()
    cerebro.addstrategy(strategy, params)
    cerebro.adddata(data)
    cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')
    back = cerebro.run()
    portfolio = back[0].analyzers.getbyname('pyfolio')
    returns, positions, transactions, gross_lev = portfolio.get_pf_items()
    returns.index = returns.index.tz_convert(None)
    if output is None:
        file_name = get_default_strategy_name(strategy, data)
        output = save_analyze_path + "\\pyfolio"
        if not os.path.exists(output):
            os.makedirs(output)
        output = output + "\\" + file_name + ".html"
    report_path = save_analyze_path + "\\html\\report.html"
    if not os.path.exists(report_path):
        report_path = None
    quantstats.reports.html(returns, output=output, template_path=report_path, download_filename=output, title=title)
    if is_show:
        webbrowser.open(output)
    path = file_util.html2img(output)
    path = file_util.compress_image(path)
    return path


def bokeh_analyze_plot(data,
                       strategy,
                       params=None,
                       output=None,
                       is_show=True):
    """
    财务分析
    """
    cerebro = actuator.get_default_cerebro()
    cerebro.addstrategy(strategy, params)
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
    if output is None:
        file_name = get_default_strategy_name(strategy, data)

        output = save_analyze_path + "\\bokeh"
        if not os.path.exists(output):
            os.makedirs(output)
        output = output + "\\" + file_name + ".html"
    if is_show:
        b = Bokeh(style='bar', scheme=Tradimo(), filename=output, output_mode="show")
    else:
        b = Bokeh(style='bar', scheme=Tradimo(), filename=output, output_mode="save")

    '【蜡烛图样式】'
    plt.style.use('seaborn')  # 使用 seaborn 主题
    plt.rcParams['figure.figsize'] = 20, 10  # 全局修改图大小
    colors = ['#729ece', '#ff9e4a', '#67bf5c', '#ed665d', '#ad8bc9', '#a8786e', '#ed97ca', '#a2a2a2', '#cdcc5d',
              '#6dccda']
    cerebro.plot(
        b,
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
    cerebro.plot(b)

    # 转图片存在bug暂时不转换
    # path = file_util.html2img(bokeh_output)
    # path = file_util.compress_image(path)
    return output
    pass

# if __name__ == '__main__':
#     data = data_util.get_local_generic_csv_data('BNB', '1h')
#     params = dict(
#         art_period=150,
#         art_low=150,
#     )
#     pyfolio_analyze_plot(data, art.AtrStrategy)
# bokeh_analyze_plot(data, art.AtrStrategy)
# name = get_default_file_name(art.AtrStrategy, data)
# print(name)
