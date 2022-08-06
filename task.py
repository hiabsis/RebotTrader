import datetime
import logging as log
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from constant import interval_corn, k_lines_csv_head
from date import BiAnService, get_k_lines
from index import execute_strategy
from setting import monitor_tasks
from strategy import SimpleMonitorStrategy

from util import generate_random_str, date2csv


def tick(**params):
    print('Tick! The time is: %s' % datetime.datetime.now(), params)


class TaskModel:
    """
    任务模型
    """

    def __init__(self, func, corn: str = "", params={}):
        """
        :param func: 任务执行的方法
        :param corn: corn表达式
        :param params:  任务参数
        """
        self.func = func
        self.corn = corn
        self.params = params
        self.id = generate_random_str()


class ParesCronTrigger(CronTrigger):
    """
    自定义的corn解析器
    """

    @classmethod
    def parse_from_crontab(cls, corn, timezone=None):
        """
        解析corn表达式
        :param corn:
        :param timezone: 时区
        :return:
        """
        values = corn.split()
        index = 0
        for value in values:
            if value == '0' or value == "*" or value == "?":
                values[index] = None
                index = index + 1

        return cls(second=values[0], minute=values[1], hour=values[2], day=values[3], month=values[4],
                   timezone=timezone)


class TaskManger:
    """
    任务管理器
    """

    def __init__(self):
        self.time_task = BlockingScheduler()
        self.biAnService = BiAnService()
        self.execute_monitor_task()

    def add_task(self, task: TaskModel):
        corns = []
        for corn in task.corn.split(" "):
            if corn == '0' or corn == "*" or corn == "?":
                corns.append(None)
            else:
                corns.append(corn)
        self.time_task.add_job(task.func, 'cron', second=corns[0], minute=corns[1], hour=corns[2], day=corns[3],
                               kwargs=task.params, id=task.id)

    def run(self):
        self.time_task.start()

    def stop(self, task_id: str):
        self.time_task.remove_job(task_id)

    def execute_monitor_task(self):
        """
        执行本地的监控任务
        :return:
        """
        for task in monitor_tasks:
            symbols = task['symbols']
            intervals = task['intervals']
            strategy = get_strategy_by_name(task['strategy'])
            for symbol in symbols:
                for interval in intervals:
                    corn = interval_corn[interval]
                    params = {
                        "symbol": symbol,
                        "interval": interval,
                        "strategy": strategy
                    }
                    task = TaskModel(monitor_task, corn, params)
                    self.add_task(task)


def monitor_task(**params):
    """
    监控任务
    :param params:
    :return:
    """
    log.info("[开始] [监控任务]  [{}-{}]".format(params['symbol'], params['interval']))
    # 获取数据
    data = get_k_lines(params['symbol'], params["interval"], 400)
    file_name = "monito_" + params['symbol'] + "_" + params["interval"]
    path = date2csv(data, file_name, k_lines_csv_head)
    # path = "D:\\work\\git\\test\\static\\data\\test.csv"
    execute_strategy(path, params['strategy'], params)
    log.info("[结束] [监控任务]  [{}-{}]".format(params['symbol'], params['interval']))


def get_strategy_by_name(clazzName: str):
    """
    通过策略的名称获取策略信息
    :param clazzName:
    :return:
    """
    if clazzName == "SimpleMonitorStrategy":
        return SimpleMonitorStrategy
    else:
        return None




