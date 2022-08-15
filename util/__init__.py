import json

from util.data_util import get_local_generic_csv_data


def to_json(data):
    return json.dumps(data, indent=4, separators=(',', ':'), ensure_ascii=False)


def get_default_strategy_name(strategy, resource):
    """
    获取默认的策略名称
    :param strategy: 策略类
    :param resource: 数据源
    :return:
    """
    return str(strategy).split('.')[-1].split('\'')[0] + "_" + str(resource._dataname).split('\\')[-1].split('.')[0]
