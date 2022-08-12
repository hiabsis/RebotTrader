project_root = "D:\\work\\git\\RebotTrader"
# 日志配置
import logging

# 日志的配置
LOG_FORMAT = "[%(levelname)s]-[%(asctime)s]-[%(pathname)s]-[%(funcName)s]-[%(lineno)d]-%(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, datefmt=DATE_FORMAT)
BINANCE_API_KEY = 'LyfDlsb6cKO6swfTqjMygvU6ByXVQb5Ip2CI1c1qDl2H70mgmAZP5eThCDNfwlc7'
BINANCE_SECRET_KEY = 'w29CUexJ0RS9DSdmtdrAFRXPpQWqDYoJGhzH5a7rzjIlAkXJ1eXEkQpZIeIDoZcw'
# 实盘
BINANCE_API_KEY_REAL = 'U8Ow8FNq11LuROI0eaR1Pg2kJVD9WlGTlvW6M6yhi3MhwLUZYBcfGAuG4J0dspxy'
BINANCE_SECRET_KEY_REAL = 'wneYhnDDYXAqF6cQ8Ngkd8aKnOpm8piktJqJC9EdvMCGZfhM3wBMZJZuPy6KRBAF'
# 工具路径

wk_img_path = project_root + "\\static\\env\\wkhtmltopdf\\bin\\wkhtmltoimage.exe"
save_analyze_path = project_root + "\\static\\analyze"
date_root_path = project_root + "\\static\\data"
image_root_path = project_root + "\\static\\images\\"
# 钉钉的群机器人token
ding_talk_monitor_robot_access_token = "a5ce65816e68fc14fa61a80085eb85bb1ca1f0610119399cb5bf8630063b7e49"
# 钉钉的群机器人密钥
ding_talk_monitor_robot_secret = "SECa8cf6e8f8b34cd02b918c072de3ca7143f2a3ea77a1d89ce978164b052fd7122"
# 钉钉的群机器人策略机器人密钥
ding_talk_strategy_robot_secret = "SEC0874bf8c3024d9e7270656da9ce3c16c38da246fdb6696dd86780498481d035a"
# 钉钉的群机器人策略机器人TOKEN
ding_talk_strategy_robot_access_token = "3e16613213fdb1409d175d5d8690c23e9794e2274ff7ccd7d151454f9aaee2d8"
# 钉钉应用
ding_talk_app_secret = "OKBWmOm6lLS1KP05s5CFYCgN8mMhkRorImNI4OQCilOFrYEdGL8ypttN35udcMDF"
# 钉钉应用
ding_talk_app_key = "dingz8mmqpd5mzx6ss69"
ding_talk_chat_id = "3d19439137fd3a3196586bdd515ef2a8"

alert_task = [
    {
        "symbol": "BTCUSDT",
        "price": [1, 2, 3],
        "isUp": True,
        "frequency": -1
    },
    {
        "symbol": "BTCUSDT",
        "price": [1, 2, 3],
        "isDown": False,
        "frequency": -1
    },

]
monitor_tasks = [
    {
        "symbols": ["BTCUSDT", "ETHUSDT"],
        "intervals": ["1m", "5m", "30m", "1h", "4h"],
        "strategy": "SimpleMonitorStrategy"
    }
]
