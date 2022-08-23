# 三种衡量价格噪音的指标：效益比率、价格密度和分形维度。
import seaborn as sns

sns.set_style("darkgrid")

import numpy as np
import matplotlib.pyplot as plt
from pylab import mpl
import pandas as pd


def cal_efficiency_ratio(ser):
    """
    效益比率
    效益比率则相反，值越大噪音越小
    价格变得幅度 / 价格累计变动幅度
    输入数据ser为价格的Series
    :param ser:
    :return:
    """
    a = abs(ser.iloc[-1] - ser.iloc[0])
    b = abs(ser - ser.shift(1)).sum()
    return a / b


def cal_price_density(df):
    """
    价格密度
    值越大噪音越大
    输入数据为包含最高、最低、收盘价的dataframe
    :param df:
    :return:
    """
    return (df.high - df.low).sum() / (df.high.max() - df.low.min())


def cal_fractal_dimension(df):
    """
    分形维度
    值越大噪音越大
    输入数据为包含最高、最低、收盘价的dataframe
    :param df:
    :return:
    """
    n = len(df)
    L = np.sqrt((1 / n) ** 2 + abs(df.close - df.close.shift(1)) / (df.high.max() - df.low.min())).sum()
    return 1 + (np.log(L) + np.log(2)) / np.log(2 * n)


mpl.rcParams['font.sans-serif'] = ['SimHei']
mpl.rcParams['axes.unicode_minus'] = False
# 模拟数据
x = np.arange(10)
y1 = 0.4 * x + 2
y2 = 0.4 * x + 2 + 0.5 * np.random.randn(10)
y3 = 0.4 * x + 2 + 1.5 * np.random.randn(10)
y2[0] = y3[0] = 0.4 * x[0] + 2
y2[-1] = y3[-1] = 0.4 * x[-1] + 2
# 可视化
plt.figure(figsize=(10, 6))
er1 = cal_efficiency_ratio(pd.Series(y1))
er2 = cal_efficiency_ratio(pd.Series(y2))
er3 = cal_efficiency_ratio(pd.Series(y3))
plt.plot(x, y1, label=f'无噪音:ER={er1}')
plt.plot(x, y2, label=f'中等噪音:ER={er2:.2f}')
plt.plot(x, y3, label=f'高等噪音:ER={er3:.2f}')
plt.xticks(range(10))
plt.legend()
print(er1)
print(er2)
print(er3)
x = np.arange(10)
y1 = x + 1.5 * np.random.randn(10)
y2 = 0.5 * x + 1.5 * np.random.randn(10)
y1[0] = y2[0] = x[0]
plt.figure(figsize=(10, 6))
er1 = cal_efficiency_ratio(pd.Series(y1))
er2 = cal_efficiency_ratio(pd.Series(y2))
print(er1)
print(er2)
plt.plot(x, y1, label=f'相对低噪声:ER={er1:.2f}')
plt.plot(x, y2, label=f'相对高噪声:ER={er2:.2f}')
plt.xticks(range(10))
plt.legend()
plt.plot()
