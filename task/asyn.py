import asyncio


class AsynTaskManage:
    """
    异步任务管理器
    """
    tasks = list()

    def add_asyn_task(self, task):
        """
        添加异步任务
        :return:
        """
        self.tasks.append(task)
        pass

    def run_asyn_task(self):
        """
        运行异步任务
        :return:
        """
        loop = asyncio.get_event_loop()
        for task in self.tasks:
            loop.run_until_complete(task.run())


class AsynTask:
    """
    异步任务
    """
    task_func = None

    def __int__(self, task_func, **kwargs):
        self.params = kwargs,
        self.task_func = task_func

    def run(self):
        self.task_func(self.params)
