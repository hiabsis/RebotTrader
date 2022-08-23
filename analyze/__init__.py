import os
import webbrowser
import backtrader as bt
import quantstats
import actuator
from backtrader_plotting import Bokeh
from backtrader_plotting.schemes import Tradimo
from setting import save_analyze_path
from util import file_util


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
    cerebro = actuator.create_default_cerebro()
    cerebro.addstrategy(strategy, params)
    cerebro.adddata(data)
    cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')
    back = cerebro.run()
    portfolio = back[0].analyzers.getbyname('pyfolio')
    returns, positions, transactions, gross_lev = portfolio.get_pf_items()
    returns.index = returns.index.tz_convert(None)
    if output is None:
        file_name = get_default_file_name(strategy, data)
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


def get_default_file_name(strategy, resource):
    return str(strategy).split('.')[-1].split('\'')[0] + "_" + str(resource._dataname).split('\\')[-1].split('.')[0]


def bokeh_analyze_plot(data,
                       strategy,
                       output=None,
                       params=None,
                       is_show=True):
    """
    财务分析
    """
    cerebro = actuator.create_default_cerebro()
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
        file_name = get_default_file_name(strategy, data)

        output = save_analyze_path + "\\bokeh"
        if not os.path.exists(output):
            os.makedirs(output)
        output = output + "\\" + file_name + ".html"
    if is_show:
        b = Bokeh(style='bar', scheme=Tradimo(), filename=output, output_mode="show")
    else:
        b = Bokeh(style='bar', scheme=Tradimo(), filename=output, output_mode="save")
    cerebro.plot(b)

    # 转图片存在bug暂时不转换
    # path = file_util.html2img(bokeh_output)
    # path = file_util.compress_image(path)
    return output
    pass



