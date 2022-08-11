import unittest

from strategy.rsj import *


class TestCase(unittest.TestCase):
    data = data_util.get_local_generic_csv_data('BTC', '1d')

    def test_something(self):
        self.assertEqual(True, True)  # add assertion here

    def test_rsj_v1(self):
        strategy.run(self.data, RsjV1Strategy, is_show=True, is_log=True)
