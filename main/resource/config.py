# 环境
ENV = "dev"

# 日志级别
LOG_LEVEL = 'INFO'
# VPN代理信息
PROXIES = {'http': 'http://127.0.0.1:7890', 'https': 'http://127.0.0.1:7890'}
# 静态资源位置
STATIC_PATH = r"D:\work\git\RebotTrader\main\resource\static"
KLINES_PATH = STATIC_PATH + r"\klines"
ANALYZE_PATH = STATIC_PATH + r"\analyze"
KLINES_HEAD = ["Time", "Open", "Close", "High", "Low", "Volume"]
