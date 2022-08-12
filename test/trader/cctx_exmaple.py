import ccxt
import setting
import schedule
import pandas as pd
import logging

pd.set_option('display.max_rows', None)

import warnings

warnings.filterwarnings('ignore')

import numpy as np
from datetime import datetime
import time

import ccxt

exchange = ccxt.binanceus({
    "apiKey": setting.BINANCE_API_KEY,
    "secret": setting.BINANCE_SECRET_KEY,
    'timeout': 15000,
    'enableRateLimit': True,
    'proxies': {'https': "http://127.0.0.1:7890", 'http': "http://127.0.0.1:7890"}
})
# 虚拟交易
exchange.set_sandbox_mode(True)


def tr(data):
    data['previous_close'] = data['close'].shift(1)
    data['high-low'] = abs(data['high'] - data['low'])
    data['high-pc'] = abs(data['high'] - data['previous_close'])
    data['low-pc'] = abs(data['low'] - data['previous_close'])

    tr = data[['high-low', 'high-pc', 'low-pc']].max(axis=1)

    return tr


def atr(data, period):
    data['tr'] = tr(data)
    atr = data['tr'].rolling(period).mean()

    return atr


def supertrend(df, period=7, atr_multiplier=3):
    # 计算指标
    # 均价
    hl2 = (df['high'] + df['low']) / 2
    # ATR
    df['atr'] = atr(df, period)
    # 价格通道上轨
    df['upperband'] = hl2 + (atr_multiplier * df['atr'])
    # 价格通道下轨
    df['lowerband'] = hl2 - (atr_multiplier * df['atr'])
    # 是否处于上升通道
    df['in_uptrend'] = True

    for current in range(1, len(df.index)):
        previous = current - 1
        # 当前收盘价大于 价格通道上轨
        if df['close'][current] > df['upperband'][previous]:
            # 目前是上升趋势
            df['in_uptrend'][current] = True
        # 收盘价格低于下轨道
        elif df['close'][current] < df['lowerband'][previous]:
            # 目前是下降趋势
            df['in_uptrend'][current] = False
        else:
            # 当前处于上升通道
            df['in_uptrend'][current] = df['in_uptrend'][previous]

            if df['in_uptrend'][current] and df['lowerband'][current] < df['lowerband'][previous]:
                df['lowerband'][current] = df['lowerband'][previous]

            if not df['in_uptrend'][current] and df['upperband'][current] > df['upperband'][previous]:
                df['upperband'][current] = df['upperband'][previous]

    return df


in_position = False


def check_buy_sell_signals(df):
    global in_position
    logging.info("checking for buy and sell signals")
    logging.info(df.tail(5))
    last_row_index = len(df.index) - 1
    previous_row_index = last_row_index - 1

    if not df['in_uptrend'][previous_row_index] and df['in_uptrend'][last_row_index]:
        logging.info("changed to uptrend, buy")
        if not in_position:
            order = exchange.create_market_buy_order('ETH/USD', 0.05)
            logging.info(order)
            in_position = True
        else:
            logging.info("already in position, nothing to do")

    if df['in_uptrend'][previous_row_index] and not df['in_uptrend'][last_row_index]:
        if in_position:
            logging.info("changed to downtrend, sell")
            order = exchange.create_market_sell_order('ETH/USD', 0.05)
            logging.info(order)
            in_position = False
        else:
            logging.info("You aren't in position, nothing to sell")


def run_bot():
    logging.info(f"Fetching new bars for {datetime.now().isoformat()}")
    # 获取行情信息
    bars = exchange.fetch_ohlcv('ETH/USDT', timeframe='1m', limit=100)
    # 解析行情信息
    df = pd.DataFrame(bars[:-1], columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    # 获取指标计算
    supertrend_data = supertrend(df)
    # 对接实盘的买卖
    check_buy_sell_signals(supertrend_data)


schedule.every(100).seconds.do(run_bot)

while True:
    schedule.run_pending()
