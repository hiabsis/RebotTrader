from hyperopt import hp

import strategy
from analyze import simple_analyze
from strategy.art import create_dynamic_atr_strategy_v2, create_dynamic_atr_strategy_v1
from util import data_util


def test_dynamic_atr_strategy_v1(params=None):
    """
    测试优化后的策略
    :return:
    """

    strategy.run_strategy(data, create_dynamic_atr_strategy_v1, params=params,
                          is_show=True)


def test_dynamic_atr_strategy_v1_opt():
    """
    测试优化后的策略
    :return:
    """
    data = data_util.get_local_generic_csv_data('BTC', '1h')
    space = dict(
        art_period=hp.randint('art_period', 10, 24 * 7),
        lines_period=hp.randint('lines_period', 24 * 7),
        continuous_period=hp.randint('continuous_period', 10),
        take_profit=hp.uniform('take_profit', 0, 0.5),
        stop_loss=hp.uniform('stop_loss', 0, 0.5),
        position=hp.uniform('position', 0, 0.5),
    )
    opt = strategy.Optimizer(data, space, create_dynamic_atr_strategy_v1, max_evals=1000,
                             strategy_name='dynamic_atr_strategy_v1',
                             is_send_ding_task=True)
    opt.run()
    opt.plot()


def test_batch_dynamic_atr_strategy_v1():
    space = dict(
        art_period=hp.randint('art_period', 10, 24 * 7),
        lines_period=hp.randint('lines_period', 24 * 7),
        continuous_period=hp.randint('continuous_period', 10),
        take_profit=hp.uniform('take_profit', 0, 0.5),
        stop_loss=hp.uniform('stop_loss', 0, 0.5),
        position=hp.uniform('position', 0, 0.5),
    )
    strategy.batch_optimizer(create_dynamic_atr_strategy_v1, space, is_send_ding_talk=True)


def test_dynamic_atr_strategy_v2():
    params = {'art_down_period': 79.69143115200198, 'art_period': 126.03169980419545,
              'art_up_period': 93.78601780350444, 'position': 0.49537855489340477, 'stop_loss': 0.33419838428248283,
              'take_profit': 0.2591238199286383}

    strategy.run_strategy(data, create_dynamic_atr_strategy_v2, params=params, is_show=True)
    simple_analyze(create_dynamic_atr_strategy_v2, params)
    pass


def test_opt_dynamic_atr_strategy_v2():
    """
    测试优化后的策略
    :return:
    """

    space = dict(
        art_period=hp.uniform('art_period', 10, 24 * 7),
        art_down_period=hp.uniform('art_down_period', 1, 24 * 7),
        art_up_period=hp.uniform('art_up_period', 1, 24 * 7),
        take_profit=hp.uniform('take_profit', 0, 0.5),
        stop_loss=hp.uniform('stop_loss', 0, 0.5),
        position=hp.uniform('position', 0, 0.5),
    )
    opt = strategy.Optimizer(data, space, create_dynamic_atr_strategy_v2,
                             max_evals=1,
                             strategy_name='dynamic_atr_strategy_v2',
                             is_send_ding_task=True)
    opt.run()
    opt.plot()


def test_batch_dynamic_atr_strategy_v2():
    space = dict(
        art_period=hp.uniform('art_period', 10, 24 * 7),
        art_down_period=hp.uniform('art_down_period', 1, 24 * 7),
        art_up_period=hp.uniform('art_up_period', 1, 24 * 7),
        take_profit=hp.uniform('take_profit', 0, 0.5),
        stop_loss=hp.uniform('stop_loss', 0, 0.5),
        position=hp.uniform('position', 0, 0.5),
    )

    strategy.batch_optimizer(create_dynamic_atr_strategy_v2, space, strategy_name='dynamic_atr_strategy_v2',
                             is_send_ding_talk=True, max_evals=300)


data = data_util.get_local_generic_csv_data('BNB', '1h')
if __name__ == '__main__':
    test_dynamic_atr_strategy_v2()
