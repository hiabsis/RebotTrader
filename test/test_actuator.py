import unittest
from util import data_util
import actuator
from strategy.good import art


class ActuatorTestCase(unittest.TestCase):
    data = data_util.get_local_generic_csv_data('BNB', '1h')

    def test(self):
        self.assertEqual(True, True)  # add assertion here

    def test_run(self):
        actuator.run(self.data, art.AtrStrategy, strategy_name="ART策略")
        self.test()


if __name__ == '__main__':
    unittest.main()
