# import datetime
#
# import setting
# import backtrader
#
# config = {
#     'apiKey': setting.BINANCE_API_KEY,
#     'secret': setting.BINANCE_SECRET_KEY,
#     'enableRateLimit': True,
# }
# store = CCXTStore(exchange='binance', currency='BUSD', config=config, retries=5, debug=False, sandbox=True)
#
# cerebro = backtrader.Cerebro(quicknotify=True)
#
# broker_mapping = {
#     'order_types': {
#         backtrader.Order.Market: 'market',
#         backtrader.Order.Limit: 'limit',
#         backtrader.Order.Stop: 'stop-loss',
#         backtrader.Order.StopLimit: 'stop limit'
#     },
#     'mappings': {
#         'closed_order': {
#             'key': 'status',
#             'value': 'closed'
#         },
#         'canceled_order': {
#             'key': 'result',
#             'value': 1}
#     }
# }
# broker = store.getbroker(broker_mapping=broker_mapping)
# cerebro.setbroker(broker)
#
# hist_start_date = datetime.datetime.utcnow() - datetime.datetime.timedelta(minutes=50)
#
# btc = store.getdata(dataname='BTC/USDT', name="BTCUSDT",
#                     timeframe=bt.TimeFrame.Minutes, fromdate=hist_start_date,
#                     compression=1, ohlcv_limit=50, drop_newest=True)
#
# eth = store.getdata(dataname='ETH/USDT', name="ETHUSDT",
#                     timeframe=bt.TimeFrame.Minutes, fromdate=hist_start_date,
#                     compression=1, ohlcv_limit=50, drop_newest=True)
#
# cerebro.adddata(btc, name='btc')
# cerebro.adddata(eth, name='eth')
# cerebro.addstrategy(BTC_ETH_Exchange_Strategy)
# cerebro.addsizer(bt.sizers.PercentSizer, percents=99.999)
# cerebro.run()
