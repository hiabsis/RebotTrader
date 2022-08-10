from hyperopt import hp

import strategy
from strategy.art import create_dynamic_atr_strategy_v2
from util import data_util


def test_dynamic_atr_strategy_v2_opt():
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


def test_batch_dynamic_atr_strategy_v2_opt():
    space = dict(
        art_period=hp.uniform('art_period', 10, 24 * 7),
        art_down_period=hp.uniform('art_down_period', 1, 24 * 7),
        art_up_period=hp.uniform('art_up_period', 1, 24 * 7),
        take_profit=hp.uniform('take_profit', 0, 0.5),
        stop_loss=hp.uniform('stop_loss', 0, 0.5),
        position=hp.uniform('position', 0, 0.5),
    )

    strategy.batch_optimizer(create_dynamic_atr_strategy_v2, space, strategy_name='dynamic_atr_strategy_v2',
                             is_send_ding_talk=True, max_evals=1)


if __name__ == '__main__':
    test_batch_dynamic_atr_strategy_v2_opt()
