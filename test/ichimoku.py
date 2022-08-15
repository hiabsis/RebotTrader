import logging
import time
import unittest

from hyperopt import hp
import asyncio
import util
import actuator

from strategy.good.ichimoku import IchimokuV1Strategy


class Case(unittest.TestCase):
    # data = util.get_local_generic_csv_data('ETH', '1h')

    # 任务

    def ichimoku_v1_strategy(self):
        params = None
        actuator.run(self.data, IchimokuV1Strategy, params)
        self.assertEqual(True, True)  # add assertion here

    def test_batch_ichimoku_v1_strategy(self):
        actuator.batch_run(IchimokuV1Strategy)

    def opt_ichimoku_v1_strategy(self):
        space = dict(
            tenkan_sen_period=hp.randint('tenkan_sen_period', 200),
            kijun_sen_period=hp.randint('kijun_sen_period', 200),
            senkou_span_a_pre=hp.randint('senkou_span_a_pre', 200),
            senkou_span_b_pre=hp.randint('senkou_span_b_pre', 200),
            senkou_span_b_period=hp.randint('senkou_span_b_period', 200),

        )
        ac = actuator.Actuator(self.data, IchimokuV1Strategy)
        ac.opt(space, 1000)

    def bach_opt_ichimoku_v1_strategy(self):
        space = dict(
            tenkan_sen_period=hp.randint('tenkan_sen_period', 200),
            kijun_sen_period=hp.randint('kijun_sen_period', 200),
            senkou_span_a_pre=hp.randint('senkou_span_a_pre', 200),
            senkou_span_b_pre=hp.randint('senkou_span_b_pre', 200),
            senkou_span_b_period=hp.randint('senkou_span_b_period', 200),

        )
        intervals = ['1d', '5m', '15m', '30m', '1h', '4h']
        symbols = ['BTC', 'ETH', 'AAVE']
        for interval in intervals:
            for symbol in symbols:
                data = util.get_local_generic_csv_data(symbol, interval)
                ac = actuator.Actuator(data, IchimokuV1Strategy)
                ac.opt(space, 500)


if __name__ == '__main__':
    unittest.main()
