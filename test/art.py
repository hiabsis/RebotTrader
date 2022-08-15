from hyperopt import hp

import strategy
from strategy.good.art import *
from util import data_util
import actuator
import analyze


def test_opt_dynamic_atr_strategy_v2():
    """
    测试优化后的策略
    :return:
    """
    data = data_util.get_local_generic_csv_data('BTC', '1h')
    space = dict(
        art_period=hp.uniform('art_period', 10, 24 * 7),
        art_down_period=hp.uniform('art_down_period', 1, 24 * 7),
        art_up_period=hp.uniform('art_up_period', 1, 24 * 7),
        take_profit=hp.uniform('take_profit', 0, 0.5),
        stop_loss=hp.uniform('stop_loss', 0, 0.5),
        position=hp.uniform('position', 0, 0.5),
    )
    opt = strategy.Optimizer(data, space, create_dynamic_atr_strategy_v2, max_evals=1000,
                             strategy_name='dynamic_atr_strategy_v2',
                             is_send_ding_task=True)
    opt.run()
    opt.plot()


def test_batch_opt_dynamic_atr_strategy_v2():
    space = dict(
        art_period=hp.uniform('art_period', 10, 24 * 7),
        art_down_period=hp.uniform('art_down_period', 1, 24 * 7),
        art_up_period=hp.uniform('art_up_period', 1, 24 * 7),
        take_profit=hp.uniform('take_profit', 0, 0.5),
        stop_loss=hp.uniform('stop_loss', 0, 0.5),
        position=hp.uniform('position', 0, 0.5),
    )

    strategy.batch_optimizer(create_dynamic_atr_strategy_v2, space, strategy_name='dynamic_atr_strategy_v2',
                             is_send_ding_talk=True, max_evals=500)


def test_dynamic_atr_strategy_v2():
    params = {
        "art_lowest_period": 95.28260781970545,
        "art_period": 64.02704141236504,
        "position": 0.9995364843544763,
        "stop_loss": 0.5121362175837294,
        "take_profit": 0.3560544958062028
    }
    # actuator.run(data, DynamicAtrStrategyV2, params=params)
    analyze.bokeh_analyze_plot(data, DynamicAtrStrategyV2, params)


def test_create_continue_down_atr_strategy():
    params = {
        "art_lowest_period": 95.28260781970545,
        "art_period": 64.02704141236504,
        "position": 0.9995364843544763,
        "stop_loss": 0.5121362175837294,
        "take_profit": 0.3560544958062028
    }
    strategy.run_strategy(data, create_continue_down_atr_strategy, params=params, is_show=True)


def test_create_dynamic_art():
    params = {
        "art_lowest_period": 95.28260781970545,
        "art_period": 64.02704141236504,
        "position": 0.9995364843544763,
        "stop_loss": 0.5121362175837294,
        "take_profit": 0.3560544958062028
    }
    strategy.run_strategy(data, params=params, create_strategy_func=create_dynamic_art, is_show=True)


data = data_util.get_local_generic_csv_data('ETH', '1h')
if __name__ == '__main__':
    test_dynamic_atr_strategy_v2()
