import time

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import tushare as ts
from pylab import mpl
import constant.config as config

sns.set_style("darkgrid")


def cal_er(ser):
    """输入数据ser为价格的Series"""
    a = abs(ser.iloc[-1] - ser.iloc[0])
    b = abs(ser - ser.shift(1)).sum()
    return a / b


def cal_pd(df):
    """输入数据为包含最高、最低、收盘价的dataframe"""
    return (df.high - df.low).sum() / (df.high.max() - df.low.min())


def cal_fd(df):
    """输入数据为包含最高、最低、收盘价的dataframe"""
    n = len(df)
    L = np.sqrt((1 / n) ** 2 + abs(df.close - df.close.shift(1)) / (df.high.max() - df.low.min())).sum()
    return 1 + (np.log(L) + np.log(2)) / np.log(2 * n)


mpl.rcParams['font.sans-serif'] = ['SimHei']
mpl.rcParams['axes.unicode_minus'] = False
# # 模拟数据
# x = np.arange(10)
# y1 = 0.4 * x + 2
# y2 = 0.4 * x + 2 + 0.5 * np.random.randn(10)
# y3 = 0.4 * x + 2 + 1.5 * np.random.randn(10)
# y2[0] = y3[0] = 0.4 * x[0] + 2
# y2[-1] = y3[-1] = 0.4 * x[-1] + 2
# # 可视化
# plt.figure(figsize=(10, 6))
# er1 = cal_er(pd.Series(y1))
# er2 = cal_er(pd.Series(y2))
# er3 = cal_er(pd.Series(y3))
# plt.plot(x, y1, label=f'无噪音:ER={er1}')
# plt.plot(x, y2, label=f'中等噪音:ER={er2:.2f}')
# plt.plot(x, y3, label=f'高等噪音:ER={er3:.2f}')
# plt.xticks(range(10))
# plt.legend()
# # plt.show()
#
# x = np.arange(10)
# y1 = x + 1.5 * np.random.randn(10)
# y2 = 0.5 * x + 1.5 * np.random.randn(10)
# y1[0] = y2[0] = x[0]
# plt.figure(figsize=(10, 6))
# er1 = cal_er(pd.Series(y1))
# er2 = cal_er(pd.Series(y2))
# plt.plot(x, y1, label=f'相对低噪声:ER={er1:.2f}')
# plt.plot(x, y2, label=f'相对高噪声:ER={er2:.2f}')
# plt.xticks(range(10))
# plt.legend()
# # plt.show()


pro = ts.pro_api(config.TUSHARE_TOKEN)


def get_index_data(code, start='20100601', end='20220719'):
    if code[0].isdigit():
        df = pro.index_daily(ts_code=code, start_date=start, end_date=end)
    else:
        df = pro.index_global(ts_code=code, start_date=start, end_date=end)
    df.index = pd.to_datetime(df.trade_date)
    df = df.rename(columns={'vol': 'volume'})
    df = (df.sort_index()).drop('trade_date', axis=1)
    return df[['open', 'high', 'low', 'close', 'volume']]


china_indexs = {'上证综指': '000001.SH', '深证成指': '399001.SZ', '沪深300': '000300.SH', '创业板指': '399006.SZ',
                '上证50': '000016.SH', '中证500': '000905.SH', '中小板指': '399005.SZ', '上证180': '000010.SH'}

global_indexs = {'恒生指数': 'HSI', '道琼斯工业指数': 'DJI', '标普500指数': 'SPX', '纳斯达克指数': 'IXIC',
                 '法国CAC40指数': 'FCHI', '德国DAX指数': 'GDAXI', '日经225指数': 'N225', '韩国综合指数': 'KS11',
                 '澳大利亚标普200指数': 'AS51', '印度孟买SENSEX指数': 'SENSEX', '台湾加权指数': 'TWII'}
# 指数合并字典
index_dict = dict(**china_indexs, **global_indexs)
# 获取全部指数价格数据
index_data = pd.DataFrame()
for name, code in index_dict.items():
    time.sleep(60)
    index_data[name] = get_index_data(code).close
index_data.to_csv('global_data.csv')


index_data = pd.read_csv('global_data.csv', index_col=0)

sss = index_data.fillna(method='ffill').dropna()
(sss / sss.iloc[0]).plot(figsize=(16, 7))
