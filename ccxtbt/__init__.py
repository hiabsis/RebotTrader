import logging

from ccxtbt.ccxtbroker import *
from ccxtbt.ccxtfeed import *
from ccxtbt.ccxtstore import *
from enum import Enum
import setting
import datetime


class OrderTypeEnum:
    BUY = 'buy',
    SELL = 'sell'


class TestStrategy(bt.Strategy):

    def __init__(self, **params):

        self.sma = bt.indicators.SMA(self.data, period=21)

    def next(self):

        # Get cash and balance
        # New broker method that will let you get the cash and balance for
        # any wallet. It also means we can disable the getcash() and getvalue()
        # rest calls before and after next which slows things down.

        # NOTE: If you try to get the wallet balance from a wallet you have
        # never funded, a KeyError will be raised! Change LTC below as approriate
        if self.live_data:
            cash, value = self.broker.get_wallet_balance('BNB')
            logging.info(f"BNB 账户情况 {cash},{value}")
            cash, value = self.broker.get_wallet_balance('BTC')
            logging.info(f"BTC 账户情况 {cash},{value}")
            cash, value = self.broker.get_wallet_balance('USDT')
            logging.info(f"USDT 账户情况 {cash},{value}")
        else:
            # Avoid checking the balance during a backfill. Otherwise, it will
            # Slow things down.
            cash = 'NA'

        for data in self.datas:
            logging.info('{} - {} | Cash {} | O: {} H: {} L: {} C: {} V:{} SMA:{}'.format(data.datetime.datetime(),
                                                                                   data._name, cash, data.open[0],
                                                                                   data.high[0], data.low[0],
                                                                                   data.close[0], data.volume[0],
                                                                                   self.sma[0]))

    def notify_data(self, data, status, *args, **kwargs):
        dn = data._name
        dt = datetime.datetime.now()
        msg = 'Data Status: {}'.format(data._getstatusname(status))
        logging.info(f'{dn} {dt} {msg}')

        if data._getstatusname(status) == 'LIVE':
            self.live_data = True
        else:
            self.live_data = False


CONFIG = {
    # 交易所API限流
    'enableRateLimit': True,
    'apiKey': setting.BINANCE_API_KEY,
    'secret': setting.BINANCE_SECRET_KEY,

}


class CcxtService:
    # 创建交易所

    __exchange = CCXTStore(exchange='binance', currency='BNB', config=CONFIG, retries=5, debug=False, sandbox=True)


    # 希望自己指定委托单的总花费
    # __exchange.options['createMarketBuyOrderRequiresPrice'] = False

    #
    def fetch_balance(self):
        balance_info = self.__exchange.fetchBalance()

        print("获取账户信息", {
            '账户资产': balance_info['total'],
            '账户现金': balance_info['free'],
            '账户持仓': balance_info['used'],
        })
        return balance_info

    def create_market_order(self, symbol, amount, order_type=OrderTypeEnum.SELL, price=None, cost=None):
        """
        市价委托
        :param cost:
        :param price:
        :param symbol:
        :param amount:
        :param order_type:
        :return:
        """
        if cost and order_type == OrderTypeEnum.BUY:
            self.__exchange.create_market_buy_order(symbol, cost)
        elif cost and order_type == OrderTypeEnum.SELL:
            self.__exchange.create_market_sell_order(symbol, cost)
        if self.__exchange.has['createMarketOrder']:
            self.__exchange.create_order(symbol, 'market', order_type, amount, price)

    def cancel_order(self, order_id):
        self.__exchange.cancel_order(order_id)

    def run_strategy(self, strategy, params=None, start=None, end=None):
        cerebro = bt.Cerebro(quicknotify=True)
        cerebro.addstrategy(strategy, kwargs=params)
        broker_mapping = {
            'order_types': {
                bt.Order.Market: 'market',
                bt.Order.Limit: 'limit',
                bt.Order.Stop: 'stop-loss',  # stop-loss for kraken, stop for bitmex
                bt.Order.StopLimit: 'stop limit'
            },
            'mappings': {
                'closed_order': {
                    'key': 'status',
                    'value': 'closed'
                },
                'canceled_order': {
                    'key': 'result',
                    'value': 1}
            }
        }

        broker = self.__exchange.getbroker(broker_mapping=broker_mapping)
        cerebro.setbroker(broker)
        hist_start_date = datetime.datetime.utcnow() - datetime.timedelta(minutes=50)
        data = self.__exchange.getdata(dataname='ETH/BUSD', name="BNBBUSD",
                                       timeframe=bt.TimeFrame.Minutes, fromdate=hist_start_date,
                                       compression=1, ohlcv_limit=50, drop_newest=True)

        cerebro.adddata(data)

        # Run the strategy
        cerebro.run()



