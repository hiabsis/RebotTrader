import os

import backtrader as bt
import quantstats

from main.infrastructure.foundation.logging import log
from main.resource.config import ANALYZE_PATH
from setting import save_analyze_path


class Analyzer:

    @staticmethod
    def pyfolio(cerebro, output, title='Returns Sentiment', ):
        """
        可视化分析 财务数据
        """
        cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')
        back = cerebro.run()
        portfolio = back[0].analyzers.getbyname('pyfolio')
        returns, positions, transactions, gross_lev = portfolio.get_pf_items()
        returns.index = returns.index.tz_convert(None)
        if output is None:
            if not os.path.exists(ANALYZE_PATH):
                os.makedirs(ANALYZE_PATH)
        output = "{}/{}.html".format(ANALYZE_PATH, output)
        report_path = save_analyze_path + "\\html\\report.html"
        if not os.path.exists(report_path):
            report_path = None
        quantstats.reports.html(returns, output=output, template_path=report_path, download_filename=output,
                                title=title)
        log.info("文件位置{} ".format(output))
        return output
