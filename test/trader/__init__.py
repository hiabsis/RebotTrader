import ccxt

# from variable id
import setting
from ccxtbt import CCXTStore
import util

exchange_id = 'binance'
exchange_class = getattr(ccxt, exchange_id)
exchange = exchange_class({
    # 交易所API限流
    'enableRateLimit': True,
    'apiKey': setting.BINANCE_API_KEY,
    'secret': setting.BINANCE_SECRET_KEY,
})
exchange.set_sandbox_mode(True)
# 载入市场清单
exchange.load_markets()
# print(exchange.id, util.to_json(exchange.load_markets()))
# 交易市场符号
# etheur1 = exchange.markets['ETH/USDT']  # get market structure by symbol
# etheur2 = exchange.market('ETH/USDT')  # same result in a slightly different way
# print(etheur1)
# etheurId = exchange.market_id('BTC/USDT')  # get market id by symbol

symbols = exchange.symbols  # get a list of symbols
print(exchange.id)
print(symbols)
symbols2 = list(exchange.markets.keys())  # same as previous line
print(symbols2)
# print all symbols

currencies = exchange.currencies  # a list of currencies
print(exchange.id)
print(currencies)

exchange.markets['BNB/USDT']  # symbol → market (get market by symbol)

# 要获得指定交易所实例的所有可用方法，包括隐含方法和统一方法，你可以 使用如下的简单代码。
doc = dir(ccxt.hitbtc())
"""
公开API包含如下内容：
    交易对
    价格流
    委托账本（L1、L2、L3...）
    交易历史（完成的订单、交易、执行）
    行情数据（现价、24小时价格）
    用于图表的OHLCV序列数据
    其他公开访问点
"""
"""
私有API
    管理个人账户信息
    查询账户余额
    委托市价单和限价单
    创建充值地址并进行账户充值
    请求提取法币和加密货币
    查询个人的敞口/完结委托单
    查询杠杆交易的位置
    获取账本历史
    在不同账户之间转账
    使用商户服务
"""
# 要获取指定交易所实例的所有可用方法
# print(dir(ccxt.hitbtc()))
# 异步调用
# import asyncio
# import ccxt.async_support as ccxt
#
#
# async def print_poloniex_ethbtc_ticker():
#     print(exchange.fetch_ticker('ETH/BTC'))


# asyncio.get_event_loop().run_until_complete(print_poloniex_ethbtc_ticker())
#
# ccxt.zaif().public_get_ticker_pair({'pair': 'btc_jpy'})  # Python
# 交易所数据结构
print("账户余额")
# print(exchange.fetchBalance())
#
# import time
#
# delay = 1  # seconds
# # 委托单
# for symbol in exchange.markets:
#     print(exchange.fetch_order_book(symbol))
#     time.sleep(delay)  # rate limit
# 市场深度
# limit = 10
# print(ccxt.binance().fetch_order_book('BTC/USD', limit))
# 委托账本聚合的层级或详情通常是数字标注的，就像L1、L2、L3...
#
# L1：较少的详情，用于快速获取非常基本的信息，也就是仅市场价格。看起来就像在委托账本中仅包含一个委托单。
# L2：最常用的聚合层级，委托单交易量按价格分组。如果两个委托单有相同的价格，那么他们会合并为一项，其总量 为这两个委托单的交易量的和。这个聚合层级可能适合大部分的应用目的。
# L3：最详细的层级，包含所有的订单，没有聚合。这一层级自然包含了输出中的重复内容。因此，如果两个订单 有相同的价格，它们也不会合并在一起，这两个订单的优先级则取决于交易所的撮合引擎。你不一定真的需要 L3详情来进行交易。实际上，大多数情况下你根本不需要这么详细的信息。因此有些交易所不支持这个级别的数据， 总是返回聚合后的委托账本。
# 如果你想获取L2委托账本，可以使用统一API中的fetchL2OrderBook(symbol, limit, params) 或 fetch_l2_order_book(symbol, limit, params)方法
# 委托账本模型的结构
# 查询市场价格
orderbook = exchange.fetch_order_book(exchange.symbols[0])
bid = orderbook['bids'][0][0] if len(orderbook['bids']) > 0 else None
ask = orderbook['asks'][0][0] if len(orderbook['asks']) > 0 else None
spread = (ask - bid) if (bid and ask) else None
print('查询市场价格')
print(exchange.id, 'market price', {'bid': bid, 'ask': ask, 'spread': spread})

# 价格行情
# 价格行情包含了最近一段时间内特定交易市场的统计信息，通常使用24小时进行统计。 查询价格行情的方法如下：
#
# fetchTicker (symbol, params = {})   // for one ticker
# fetchTickers (symbol, params = {})  // for all tickers at once
# 检查交易所的exchange.has['fetchTicker']和 exchange.has['fetchTickers']属性 来决定所查询的交易所是否支持这些方法
import random

print('按交易对查询实时行情')
if (exchange.has['fetchTicker']):
    print(exchange.fetch_ticker('BTC/USDT'))  # ticker for LTC/ZEC
    symbols = list(exchange.markets.keys())
    print(exchange.fetch_ticker(random.choice(symbols)))  # ticker for a random symbol

# 查询所有交易对的实时行情
print('查询所有交易对的实时行情')
if (exchange.has['fetchTickers']):
    print(exchange.fetch_tickers())  # all tickers indexed by their symbols

print('OHLCV烛线图')
import time

if exchange.has['fetchOHLCV']:
    for symbol in exchange.markets:
        time.sleep(exchange.rateLimit / 1000)  # time.sleep wants seconds
        print(symbol, exchange.fetch_ohlcv(symbol, '1d'))  # one day


# 实时行情数据结构
# k_lines= {
#     'symbol':       [] ,# string symbol of the market ('BTC/USD', 'ETH/BTC', ...)
#     'info':        { the original non-modified unparsed reply from exchange API },
#     'timestamp':     int (64-bit Unix Timestamp in milliseconds since Epoch 1 Jan 1970)
#     'datetime':      ISO8601 datetime string with milliseconds
#     'high':          float, // highest price
#     'low':           float, // lowest price
#     'bid':           float, // current best bid (buy) price
#     'bidVolume':     float, // current best bid (buy) amount (may be missing or undefined)
#     'ask':           float, // current best ask (sell) price
#     'askVolume':     float, // current best ask (sell) amount (may be missing or undefined)
#     'vwap':          float, // volume weighed average price
#     'open':          float, // opening price
#     'close':         float, // price of last trade (closing price for current period)
#     'last':          float, // same as `close`, duplicated for convenience
#     'previousClose': float, // closing price for the previous period
#     'change':        float, // absolute change, `last - open`
#     'percentage':    float, // relative change, `(change/open) * 100`
#     'average':       float, // average price, `(last + open) / 2`
#     'baseVolume':    float, // volume of base currency traded for last 24 hours
#     'quoteVolume':   float, // volume of quote currency traded for last 24 hours
# }

book = {
    # bids数组按价格降序排列，最高的买入价格排在第一个，最低的 买入价格排在最后
    # bids/asks数组可以是空的，表示交易所的委托账本中没有相应 的委托单。
    'bids': [

    ],
    'asks': [

    ],
    'timestamp': 1499280391811,
    'datetime': '2017-07-05T18:47:14.692Z',
}

trader_setting = {
    'id': 'exchange',
    'name': 'Exchange',
    'countries': ['US', 'CN', 'EU'],
    'urls': {
        'api': 'https://api.example.com/data',
        'www': 'https://www.example.com',
        'doc': 'https://docs.example.com/api',
    },
    'version': 'v1',
    'api': {},
    #  描述交易所特性支持能力的关联数组，
    'has': {
        'CORS': False,
        'publicAPI': True,
        'privateAPI': True,
        'cancelOrder': True,
        'createDepositAddress': False,
        'createOrder': True,
        'deposit': False,
        'fetchBalance': True,
        'fetchClosedOrders': False,
        'fetchCurrencies': False,
        'fetchDepositAddress': False,
        'fetchMarkets': True,
        'fetchMyTrades': False,
        'fetchOHLCV': False,
        'fetchOpenOrders': False,
        'fetchOrder': False,
        'fetchOrderBook': True,
        'fetchOrders': False,
        'fetchStatus': 'emulated',
        'fetchTicker': True,
        'fetchTickers': False,
        'fetchBidsAsks': False,
        'fetchTrades': True,
        'withdraw': False,
    },
    'timeframes': {  # 交易所的fetchOHLCV方法支持的时间尺度
        '1m': '1minute',
        '1h': '1hour',
        '1d': '1day',
        '1M': '1month',
        '1y': '1year',
    },
    'timeout': 10000,  # ccxt访问交易所API时，请求-响应的超时设置，单位：毫秒
    'rateLimit': 2000,  # 交易所API的请求限流
    # 是否启用内置的限流机制
    'enableRateLimit': False,
    #  用于设置HTTP请求头中的User-Agent
    'userAgent': 'ccxt/1.1.1 ...',
    # 是否记录HTTP请求信息到标准输出设备
    'verbose': False,
    # : 市场描述关联数组，键为交易对或交易符号
    'markets': {...},
    # 交易所的有效符号的数组，以字母表顺序排列
    'symbols': [...],
    # 交易所的有效数字货币的关联数组，键为数字货币的代码（3~4字母）
    'currencies': {...},
    # 按交易所列举的市场关联数值。在访问此属性之前需要先载入市场
    'markets_by_id': {...},
    # 用来访问交易所的http(s)代理的URL字符串，
    'proxy': 'https://crossorigin.me/',
    # 用来访问交易所的API Key。
    'apiKey': '92560ffae9b8a0421...',
    # 用来访问交易所的密文。
    'secret': '9aHjPmW+EtRRKN/Oi...',
    # 交易所要求的交易密码
    'password': '6kszf4aci8r',
    # 你的交易所账户的唯一ID
    'uid': '123456',
}

market = {
    'id': ' btcusd',  # 用来在交易所内区分不同市场的字符串或数字ID
    'symbol': 'BTC/USD',  # 市场符号，用来表示交易对的大写的字符串代码
    'base': 'BTC',  # ：基础货币代码，表示基础法币或加密货币的统一的大写字符串代码，代码是标准化的
    'quote': 'USD',  # 报价货币代码，用来表示报价法币或数字货币的统一的大写字符串代码。
    'baseId': 'btc',  # 基础货币ID，是交易所特定的表示基础货币的ID，不是统一的代码，理论上可以是任何 字符串
    'quoteId': 'usd',  # 报价货币ID，是交易所特定的表示报价货币的ID，也不是统一的代码，每个交易所自行维护。
    'active': True,  # 是否激活，布尔值，表示这个市场是否可交易。通常如果一个市场未激活，那么所有相关的 行情、委托账本以及其他访问端结点都返回空响应、全零、无数据或过时数据
    # 调用者需要检查市场 是否激活并且定期刷新市场缓存。
    # 在委托单中金额相关字段（例如价格、数量、成本等）支持的最大小数位数
    'precision': {
        'price': 8,
        'amount': 8,
        'cost': 8,
    },
    # 限值，价格、数量和成本等的最高和最低限值，其中：成本 = 价格 * 数量。
    'limits': {
        'amount': {
            'min': 0.01,
            'max': 1000,
        },
        'cost': {...},
    },
    # 一个用于记录非共性市场属性的关联数组，包括手续费、费率、限制以及其他一般性市场信息
    # 内部的info数组对每个特定的市场都是不同的，其内容依赖于交易所

    'info': {...},
}
