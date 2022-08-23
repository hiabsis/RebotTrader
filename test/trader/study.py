import ccxt
import setting
import util

# 创建交易所
exchange_id = 'binance'
exchange_class = getattr(ccxt, exchange_id)
exchange = exchange_class({
    # 交易所API限流
    'enableRateLimit': True,
    'apiKey': setting.BINANCE_API_KEY,
    'secret': setting.BINANCE_SECRET_KEY,
})
# 模拟交易
exchange.set_sandbox_mode(True)
# 获取账户信息
balance = exchange.fetchBalance()

print("获取账户信息")

balance_info = {
    '账户资产': balance['total'],
    '账户现金': balance['free'],
    '账户持仓': balance['used'],

}
print(util.to_json(balance_info))
print()
print('查询委托单')

if 'fetchOrders' in exchange.has:
    order = exchange.fetchOrders('BTC/USDT')
    print(util.to_json(order))

print('获取历史交易')
if 'fetchTrades' in exchange.has:
    trades = exchange.fetchTrades('BTC/USDT', limit=1)
    print(util.to_json(trades))
print('查询全部委托单')
if exchange.has['fetchOrders']:
    exchange.fetchOrders(symbol='BNB/USDT', since=None, limit=1, params={})
    print(util.to_json(trades))

