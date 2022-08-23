from hyperopt import hp
import actuator.optimizer as op
import actuator

import strategy.keltner_channel as kc
import data as ds

if __name__ == '__main__':
    # data = du.get_local_generic_csv_data('ETH', '1h')
    start_time = '2022-01-01'
    end_time = '2022-07-15'
    data = ds.CoinService.load_default_generic_csv_data('ETH', '1h', start_time, end_time)
    actuator.run(data, kc.KeltnerChannelStrategy)
    space = dict(
        kc_ema=hp.randint('kc_ema', 300),
        kc_atr=hp.randint('kc_ema', 300),
    )
    # op.Optimizer(data, space, )
