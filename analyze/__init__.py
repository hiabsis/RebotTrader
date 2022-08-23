import os

import backtrader
import webbrowser
import backtrader as bt
import pandas
import pyfolio
import quantstats
import webbrowser

import matplotlib.pyplot as plt
import quantstats
import actuator
from backtrader_plotting import Bokeh
from backtrader_plotting.schemes import Tradimo
from matplotlib import ticker

from setting import save_analyze_path

from util import file_util, get_default_strategy_name
import actuator
from util import file_util


def simple_analyze(cerebro, name="DEFAULT_NAME"):
    """
    对策略分析
    :param name:
    :return:
    """

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
    fig.tight_layout()  # 规整排版
    plt.show()


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


def get_default_file_name(strategy, resource):
    return str(strategy).split('.')[-1].split('\'')[0] + "_" + str(resource._dataname).split('\\')[-1].split('.')[0]


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



