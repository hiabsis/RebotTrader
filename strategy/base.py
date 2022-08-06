# import datetime
# import os
# from json import dumps
#
# import backtrader as bt
# import numpy as np
# import pandas as pd
# from backtrader import Cerebro, OptReturn, Strategy
# from backtrader.analyzers import SharpeRatio, DrawDown, Returns, AnnualReturn, Transactions, TradeAnalyzer, TimeReturn
# from backtrader.sizers import PercentSizer
# from pandas import DataFrame
#
# from setting import date_root_path
# from utils import load_csv_data, add_mouth, send_text_to_dingtalk, to_json
# import optunity as optunity
#
#
# class BaseStrategy(bt.Strategy):
#     is_log = False
#     name = ""
#
#     def get_strategy_name(self):
#         return self.name
#
#     def is_show_log_info(self, is_show):
#         self.is_log = is_show
#
#     def log(self, message, doprint=False):
#         if self.is_log or doprint:
#             print('[{}] [{}]'.format(bt.num2date(self.data.datetime[0]), message))
#         pass
#
#     def notify_order(self, order):
#         if order.status in [bt.Order.Submitted, bt.Order.Accepted]:
#             return
#         if order.status == order.Completed:
#             if order.isbuy():
#                 log_txt = '买:%.2f  量:%s  持仓:%s' % (order.executed.price, order.executed.size, self.position.size)
#                 self.log(log_txt)
#             else:
#                 log_txt = '卖:%.2f 量:%s  持仓:%s' % (order.executed.price, order.executed.size, self.position.size)
#                 self.log(log_txt)
#         if order.status in [bt.Order.Close]:
#             log_txt = '平:%.2f 量:%s  持仓:%s' % (order.executed.price, order.executed.size, self.position.size)
#             self.log(log_txt)
#
#     @staticmethod
#     def set_params(c: Cerebro, params):
#         """
#         设置策略参数
#         :param c:
#         :param params:
#         :return:
#         """
#         return c
#
#
# def create_cerebro(cash=10000.0, commission=0.01, stake=1, strategy=None):
#     """
#     :param data: 数据
#     :param cash: 初始资金
#     :param commission: 佣金率
#     :param stake: 交易单位大小
#     :param strategy: 交易策略
#     :return:
#     """
#     cerebro = bt.Cerebro()
#     # 设置启动资金
#     cerebro.broker.setcash(cash)
#     # 设置交易单位大小
#     cerebro.addsizer(bt.sizers.FixedSize, stake=stake)
#     # 设置佣金率为千分之一
#     cerebro.broker.setcommission(commission)
#     # 显示回测过程中的买入和卖出信号
#     cerebro.addobserver(bt.observers.Value)
#     # 显示了回测过程中的买入和卖出信号
#     cerebro.addobserver(bt.observers.BuySell)
#     return cerebro
#
#
# class Optimizer:
#     name = ""
#
#     def get_name(self):
#         return self.name
#
#     def run(self):
#         pass
#
#     def set_cash(self, cash):
#         pass
#
#     def get_optimal_parameters(self):
#         pass
#
#     def set_data(self, data):
#         pass
#
#     def get_optimize_total_assets(self):
#         pass
#
#
# class MainApp:
#
#     def __init__(self):
#         self.data = None
#         self.optimizer = None
#         self.cash = 10 * 1000
#         self.cerebro = create_cerebro(cash=self.cash)
#         self.fuc = None
#         self.params = None
#
#     def set_params(self, params):
#         self.params = params
#
#     def set_fuc(self, fuc):
#         self.fuc = fuc
#
#     def set_optimizer(self, optimizer: Optimizer):
#         self.optimizer = optimizer
#
#     def add_data(self, data):
#         self.data = data
#
#     def get_data(self):
#         return self.data
#
#     def run(self, is_show_plot=False, params=None):
#         print("初始资金", self.cash)
#         cerebro = create_cerebro(self.cash)
#         cerebro.adddata(self.data)
#         cerebro = self.fuc(cerebro, params)
#         cerebro.run()
#         print("期末资金", cerebro.broker.getvalue())
#         if is_show_plot:
#             cerebro.plot()
#
#     def run_optimizer(self, is_show_plot=False):
#         print("优化器 start ")
#         self.optimizer.set_data(self.get_data())
#         self.optimizer.run()
#         params = self.optimizer.get_optimal_parameters()
#         print("最优参数", params)
#         print("优化器 end")
#         if is_show_plot:
#             self.run(is_show_plot=True, params=params)
#         return params
#
#     def verify_optimizer(self, path, mouth=12, cash=10000):
#         data = pd.read_csv(path)
#         data = np.array(data)
#         start_time = datetime.datetime.strptime(data[0][0], "%Y-%m-%d %H:%M:%S")
#         stop_time = datetime.datetime.strptime(data[len(data) - 1][0], "%Y-%m-%d %H:%M:%S")
#         end_time = add_mouth(start_time, mouth)
#         save_params = []
#         data = load_csv_data(path, start_time, end_time)
#
#         self.optimizer.set_data(data)
#         self.optimizer.run()
#         params = self.optimizer.get_optimal_parameters()
#         message = f"验证参数优化 {self.optimizer.get_name()}"
#         send_text_to_dingtalk(message)
#         while True:
#             save_params.append(self.optimizer.get_optimal_parameters())
#             start_time = add_mouth(start_time, mouth)
#             end_time = add_mouth(end_time, mouth)
#
#             is_end = end_time.timestamp() >= stop_time.timestamp() or start_time.timestamp() >= stop_time.timestamp()
#             if is_end:
#                 break
#             cerebro = create_cerebro(cash)
#             cerebro = self.fuc(cerebro, params)
#             cerebro.run()
#             data = load_csv_data(path, start_time, end_time)
#             total_assert = self.optimizer.get_optimize_total_assets()
#             message = f"开始时间：{start_time} 结束时间 {end_time}\n" + \
#                       f"数据来源：{path}\n" + \
#                       f"初始资金:{cash}\n" + \
#                       f"期末资金：{total_assert}\n" + \
#                       f"年化率：{total_assert / cash}\n" + \
#                       f"策略参数：{dumps(params)}"
#             send_text_to_dingtalk(message)
#             cash = total_assert
#             self.optimizer.set_cash(cash)
#             self.optimizer.set_data(data)
#             self.optimizer.run()
#             params = self.optimizer.get_optimal_parameters()
#
#     def set_cash(self, cash):
#         self.cerebro.broker.set_cash(cash)
#
#
# """
#
# """
#
#
# def run_strategy(set_strategy_func, data=None, path=None, strategy_params=None, log_info={}, is_show=False):
#     if data is None:
#         data = load_csv_data(path)
#     cerebro = create_cerebro()
#     cerebro.adddata(data)
#     cerebro = set_strategy_func(cerebro, strategy_params)
#     cash = cerebro.broker.getcash()
#     cerebro.run()
#     value = cerebro.broker.getvalue()
#     data = np.array(pd.read_csv(path))
#     start = data[0][0]
#     end = data[len(data) - 1][0]
#     log_info["数据"] = path
#     log_info['开始时间'] = start
#     log_info['结束时间'] = end
#     log_info['初始资金'] = cash
#     log_info['期末资金'] = value
#     log_info['收益率'] = value / cash
#     print(to_json(log_info))
#     if is_show:
#         cerebro.plot()
#     return cerebro
#
#
# def run_batch_strategy(set_strategy_func, strategy_params=None, info={}, cash=10000):
#     files = os.listdir(date_root_path)
#     for file in files:
#         file_name = file.split(".")[0]
#         file_path = date_root_path + file
#         data = load_csv_data(file_path)
#         cerebro = create_cerebro(cash=cash)
#         cerebro.adddata(data)
#         cerebro = set_strategy_func(cerebro, strategy_params)
#         cash = cerebro.broker.getcash()
#         cerebro.run()
#         value = cerebro.broker.getvalue()
#         log_info = info.copy()
#         data = np.array(pd.read_csv(file_path))
#         start = data[0][0]
#         end = data[len(data) - 1][0]
#         log_info["数据"] = file_name
#         log_info['开始时间'] = start
#         log_info['结束时间'] = end
#         log_info['初始资金'] = cash
#         log_info['期末资金'] = value
#         log_info['收益率'] = value / cash
#         print(to_json(log_info))
#
#
# def run_optimizer(strategy_func, data=None, path=None, info={}, is_show=False, is_send_dingtalk=False):
#     run_start = datetime.datetime.now().timestamp()
#     if data is None:
#         data = load_csv_data(path)
#     optimizer = Optimizer(data = data)
#     optimizer.set_data(data)
#     strategy_params = optimizer.run()
#     cerebro = create_cerebro()
#     cerebro.adddata(data)
#     cerebro = strategy_func(cerebro, strategy_params)
#     cash = cerebro.broker.getcash()
#     cerebro.run()
#     value = cerebro.broker.getvalue()
#     data = np.array(pd.read_csv(path))
#     start = data[0][0]
#     end = data[len(data) - 1][0]
#     run_end = datetime.datetime.now().timestamp()
#     info["数据 |"] = path
#     info['运行时间| '] = run_end - run_start
#     info['开始时间| '] = start
#     info['结束时间|'] = end
#     info['初始资金|'] = cash
#     info['期末资金|'] = value
#     info['收益率|'] = value / cash
#     info['参数|'] = strategy_params
#     print(to_json(info))
#     if is_show:
#         cerebro.plot()
#     if is_send_dingtalk:
#         send_text_to_dingtalk(info)
#
#
# def run_verify_optimizer(path, set_strategy_func, opt, period=12, info={}, is_show=False,
#                          is_send_dingtalk=False, cash=10000):
#     log_info = info.copy()
#     log_info["任务开始时间"] = datetime.datetime.now()
#     if is_send_dingtalk:
#         send_text_to_dingtalk("校验参数有效性\n" + to_json(log_info))
#     run_start = datetime.datetime.now().timestamp()
#     data = pd.read_csv(path)
#     data = np.array(data)
#     start_time = datetime.datetime.strptime(data[0][0], "%Y-%m-%d %H:%M:%S")
#     stop_time = datetime.datetime.strptime(data[len(data) - 1][0], "%Y-%m-%d %H:%M:%S")
#     end_time = add_mouth(start_time, period)
#     data = load_csv_data(path, start_time, end_time)
#     optimizer = opt()
#     optimizer.set_data(data)
#     params = optimizer.run()
#     info['task'] = "verify_optimizer"
#
#     while True:
#         start_time = add_mouth(start_time, period)
#         end_time = add_mouth(end_time, period)
#         is_end = end_time.timestamp() >= stop_time.timestamp() or start_time.timestamp() >= stop_time.timestamp()
#         if is_end:
#             break
#         # 运行策略
#         data = load_csv_data(data_path=path, start=start_time, end=end_time)
#         cerebro = run_strategy(data=data, set_strategy_func=set_strategy_func, strategy_params=params)
#         run_end = datetime.datetime.now().timestamp()
#         total_assert = cerebro.broker.getvalue()
#         cash = total_assert
#         info["数据 |"] = path
#         info['运行时间| '] = run_end - run_start
#         info['开始时间| '] = start_time
#         info['结束时间|'] = end_time
#         info['初始资金|'] = cash
#         info['期末资金|'] = total_assert
#         info['收益率|'] = total_assert / cash
#         info['参数|'] = params
#         if is_send_dingtalk:
#             send_text_to_dingtalk(to_json(info))
#         run_start = datetime.datetime.now()
#     if is_send_dingtalk:
#         send_text_to_dingtalk("任务结束")
#     pass
#
#
#
#
#
#
#
#
#
#
#
