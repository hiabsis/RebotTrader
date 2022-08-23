import datetime
import os.path

import data.stock as stock
import data.coin as coin


class StockService:
    """
    股数据服务
    """

    @classmethod
    def download_or_update(cls, stocks: list = None, frequencys: list = None):
        """
        数据更新
        :param stocks:
        :param frequencys: stock.FrequencysEnum
        :return:
        """

        s_frequencys = []
        for frequency in frequencys:
            s_frequencys.append(frequency.value)

        stock.update_date(stocks, s_frequencys)

    @classmethod
    def get_local_path(cls, stock_code, frequency):
        """
        获取数据所在路径
        :param stock_code:
        :param frequency:
        :return:
        """
        return stock.get_stock_path(stock_code, frequency.value, resource=stock.ResourceEnum.BAOSTOCK.value)


class CoinService:
    """
    虚拟货币数据服务
    """

    @classmethod
    def get_local_path(cls, symbol: str, interval: str):
        """
        获取虚拟币所在路径
        :param symbol:
        :param interval:
        :return:
        """
        return coin.get_local_file_path(symbol, interval)

    @classmethod
    def download_or_update(cls, symbol: str, interval: str):
        return coin.down_load_data(symbol, interval)

    @classmethod
    def load_default_generic_csv_data(cls, symbol: str, interval: str, start=None, end=None, is_update=False):
        """
        加载数据
        :param symbol:
        :param interval:
        :param start:
        :param end:
        :param is_update:
        :return:
        """
        if start is None:
            start = None
        else:
            start = datetime.datetime.strptime(start, '%Y-%m-%d')
        if end is None:
            end = None
        else:
            end = datetime.datetime.strptime(end, '%Y-%m-%d')
        if is_update:
            coin.down_load_data(symbol, interval)
        path = coin.get_local_file_path(symbol, interval)
        if not os.path.exists(path):
            coin.down_load_data(symbol, interval)
        return coin.load_generic_csv_data(path, interval, start, end)
