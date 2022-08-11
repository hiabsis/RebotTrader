from strategy.art import create_dynamic_atr_strategy_v2
from util import data_util
import strategy
import analyze


def test_simple_analyze_polt():
    data = data_util.get_local_generic_csv_data('BTC', '1h')
    analyze.simple_analyze_polt(create_strategy_fun=create_dynamic_atr_strategy_v2, data=data)


if __name__ == '__main__':

    test_simple_analyze_polt()
