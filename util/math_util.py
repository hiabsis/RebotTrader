##
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import leastsq
from scipy.stats import pearsonr
import pandas as pd


def least_squares_lines(Xi, Yi, is_show=False):
    """
    最小二乘法 拟合直线
    :return:
    """
    p0 = [1, 1]
    Para = leastsq(_lines_func, p0, args=(Xi, Yi))

    k, b = Para[0]
    if is_show:
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.figure(figsize=(8, 6))
        plt.scatter(Xi, Yi, color="green", label="样本数据", linewidth=2)

        x = np.array([1, 2, 3])
        y = k * x + b
        plt.plot(x, y, color="red", label="拟合直线", linewidth=2)
        plt.title('y={}+{}x'.format(b, k))
        plt.legend(loc='lower right')
        plt.show()
    return k, b


def _lines(p, x):
    k, b = p
    return k * x + b


def _lines_func(p, x, y):
    return _lines(p, x) - y


def pearson(x: list, y: list):
    """
    Pearson 相关系数
    :param x:
    :param y:
    :return:
    """
    x1 = pd.Series(x)
    y1 = pd.Series(y)
    p = pearsonr(x1, y1)
    return p.statistic




