from typing import List

# 拟合曲线
import numpy as np
from scipy.optimize import leastsq


class MathUtil:

    @staticmethod
    def least_square_method(xi: List, yi: List):
        x = np.array(xi)
        # 体重数据
        y = np.array(yi)
        p0 = [1, 20]
        # 把error函数中除了p0以外的参数打包到args中,leastsq()为最小二乘法函数
        pera = leastsq(error, p0, args=(x, y))
        # 读取结果
        k, b = pera[0]
        return k, b


def lines(p, x):
    k, b = p
    return k * x + b


# 偏差函数，x，y为数组中对应Xi,Yi的值
def error(p, x, y):
    return lines(p, x) - y



