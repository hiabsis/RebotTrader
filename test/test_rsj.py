import unittest

import strategy.good.rsj as rsj
from util import data_util
import actuator


class TestCase(unittest.TestCase):
    data = data_util.get_local_generic_csv_data('BTC', '1d')

    def test_something(self):
        self.assertEqual(True, True)  # add assertion here

    def test_rsj_v1(self):
        actuator.run(self.data, rsj.RSJV1Strategy)
