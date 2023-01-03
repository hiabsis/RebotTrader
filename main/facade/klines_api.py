from main.infrastructure.rpc.binance.client import BinanceClint
from main.infrastructure.utils.date import INTERVAL_SECOND_DICT


def download_klines(intervals=None, symbols=None):
    if symbols is None:
        symbols = BinanceClint.query_symbols()

    if intervals is None:
        intervals = INTERVAL_SECOND_DICT.keys()

    for symbol in symbols:
        for interval in intervals:
            BinanceClint.download_kline(symbol, interval)



download_klines()