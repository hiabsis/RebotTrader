from backtrader_plotting import Bokeh
from bokeh.io import   output_file
import backtrader as bt
import quantstats

from setting import save_analyze_path
from strategy.bool import BollStrategy


def bokeh_cerebro_plot(cerebro: bt.Cerebro, save_name="bt_bokeh_plot"):
    cerebro.run(optreturn=False, tradehistory=True)
    path = save_analyze_path + "\\" + save_name + ".html"
    b = Bokeh(style='bar', tabs='multi', filename=path)  # 黑底，多页
    output_file(filename=save_name + ".html", mode='relative', title=save_name, root_dir=save_analyze_path)
    cerebro.plot(b)


def quantstats_cerebro_plot(cerebro: bt.Cerebro, name="bt_bokeh_plot.html", strategy_name=""):
    results = cerebro.run()
    print(type(results))# execute
    print((len(results)))
    back = results[0]
    pyfoliozer = back.analyzers.getbyname('pyfolio')
    returns, positions, transactions, gross_lev = pyfoliozer.get_pf_items()
    returns.index = returns.index.tz_convert(None)
    quantstats.reports.html(returns, output='fstatss.html', download_filename='fstatss.html', title='Returns Sentiment')
    return


if __name__ == '__main__':
    cerebro = bt.Cerebro()
    # 设置启动资金
    cerebro.broker.setcash(100000.0)
    # 设置佣金为零
    cerebro.broker.setcommission(commission=0.001)
    idx = cerebro.addstrategy(BollStrategy, period=130)  # 添加策略

    cerebro.addanalyzer(bt.analyzers.SharpeRatio)
    cerebro.addobserver(bt.obs.Broker)
    cerebro.addobserver(bt.obs.Trades)
    #
    print('初始资金: %.2f' % cerebro.broker.getvalue())
    # bokeh_cerebro_plot(cerebro, save_name="BollStrategy")
    quantstats_cerebro_plot(cerebro, "", strategy_name="BOOL")
    print('最终资金: %.2f' % cerebro.broker.getvalue())
