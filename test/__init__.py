from binance.spot import Spot as Client

proxies = {'https': 'http://127.0.0.1:7890'}

client = Client(proxies=proxies)
print(client.time())
# Get klines of BTCUSDT at 1m interval
print(client.klines("BTCUSDT", "1m"))
# Get last 10 klines of BNBUSDT at 1h interval
print(client.klines("BNBUSDT", "1h", limit=10))
