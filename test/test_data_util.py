import constant
from util import data_util


def test_load_data():
    symbol = 'BTC'
    interval = '1h'
    data_util.down_load_data(symbol, interval)


def test_bath_down_load_data():
    symbols = constant.coin_symbol
    intervals = ['1d', '5m', '15m', '30m', '1h', '4h']
    data_util.bath_down_load_data(symbols, intervals)


if __name__ == '__main__':
    test_bath_down_load_data()
