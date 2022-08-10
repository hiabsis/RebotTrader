##
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import leastsq


def least_squares_lines(Xi, Yi, is_show=False):
    """
    最小二乘法 拟合直线
    :return:
    """
    p0 = [1, 1]
    Para = leastsq(lines_func, p0, args=(Xi, Yi))

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


def lines(p, x):
    k, b = p
    return k * x + b


def lines_func(p, x, y):
    return lines(p, x) - y


if __name__ == '__main__':
    for i in range(5):
        print(i)
    # least_squares_lines(Xi, Yi, is_show=True)
