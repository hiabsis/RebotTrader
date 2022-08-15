##最小二乘法
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import leastsq

plt.rcParams['font.sans-serif'] = ['SimHei']

Xi = np.array([1, 2, 3, 2])
Yi = np.array([1, 3, 3, 5])


def func(p, x):
    print(p)
    print(type(p))
    k, b = p
    return k * x + b


def error(p, x, y):
    return func(p, x) - y


p0 = [1, 1]

Para = leastsq(error, p0, args=(Xi, Yi))

k, b = Para[0]
print("k=", k, "b=", b)
print("cost：" + str(Para[1]))
print("求解的拟合直线为:")
print("y=" + str(round(k, 2)) + "x+" + str(round(b, 2)))
print("k", k)

plt.figure(figsize=(8, 6))
plt.scatter(Xi, Yi, color="green", label="样本数据", linewidth=2)

x = np.array([1, 2, 3])
y = k * x + b
plt.plot(x, y, color="red", label="拟合直线", linewidth=2)
plt.title('y={}+{}x'.format(b, k))
plt.legend(loc='lower right')
plt.show()
