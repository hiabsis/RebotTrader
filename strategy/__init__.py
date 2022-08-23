import strategy.keltner_channel as keltner_channel


def get_strategy_name(strategy, data=None):
    """
    获取策略名称
    :param strategy:
    :param data:
    :return:
    """
    if data is None:
        return str(strategy).split('.')[-1].split('\'')[0]
    return str(strategy).split('.')[-1].split('\'')[0] + "_" + str(data._dataname).split('\\')[-1].split('.')[0]
