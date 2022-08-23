"""
数据获取的代码
"""
import json
import os
import time

import baostock as bs
import datetime
import sys

from enum import Enum
import numpy
import pandas
import pandas as pd
import backtrader as bt
# 数据保存的根目录位置
from constant.config import DATA_ROOT_DIR, TUSHARE_TOKEN
import common as cm
import tushare as ts

# BaoStock日线数据字段
BAOSTOCK_DAY_FIELDS = 'date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,' \
                      'pctChg,isST '
# BaoStock分钟线数据字段
BAOSTOCK_MINUTE_FIELDS = "date,time,code,open,high,low,close,volume,amount,adjustflag"
# BaoStock 周月线指标
BAOSTOCK_WEEKS_FIELDS = "date,code,open,high,low,close,volume,amount,adjustflag,turn,pctChg"

# tushare 大盘指数每日指标
TUSHARE_INDEX_FIELDS = 'ts_code,trade_date,turnover_rate,pe,pe_ttm,pb,turnover_rate,turnover_rate_f,free_share,' \
                       'float_share,total_share,float_mv,total_mv '


class FrequencysEnum(Enum):
    DAY = 'd'
    FIVE_MINUTE = '5'
    FIFTEEN_MINUTE = '15'
    THIRTY_MINUTE = '30'
    ONE_HOUR = '60'


class ResourceEnum(Enum):
    BAOSTOCK = 'baostock'
    TUSHARE = 'tushare'


def get_stock_path(stock_code, frequency, resource='baostock'):
    """
    股票的保存路径
    :param resource:
    :param stock_code:
    :param frequency:
    :return:
    """
    if resource == 'baostock':
        return DATA_ROOT_DIR + f"\\{resource}\\{frequency}\\{stock_code}.csv"
    raise FileExistsError(f'resource can not find for {resource}')


def read_json(path, name=None):
    """
    读取json 数据
    :param path:
    :param name:
    :return:
    """
    if name:
        return json.load(open(path, 'r', encoding="utf-8"))[name]
    return json.load(open(path, 'r', encoding="utf-8"))


def write_json(outdir, filename, load_dict):
    """
    文件写入json
    :param outdir:
    :param filename:
    :param load_dict:
    :return:
    """
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    with open(outdir + "\\" + filename, 'w') as write_f:
        write_f.write(json.dumps(load_dict, indent=4, ensure_ascii=False))


def get_stock_codes(date=None, resource='baostock'):
    """
    获取指定日期的A股代码列表

    若参数date为空，则返回最近1个交易日的A股代码列表
    若参数date不为空，且为交易日，则返回date当日的A股代码列表
    若参数date不为空，但不为交易日，则打印提示非交易日信息，程序退出

    :param resource: 数据源
    :param date: 日期
    :return: A股代码的列表
    """
    if resource == 'baostock':
        return get_stock_codes_from_baostock(date)
    elif resource == 'tushare':
        return get_stock_codes_from_tushare()


def get_stock_codes_from_tushare():
    """
    获取tushare的股票列表
    :return:
    """

    codes_path = DATA_ROOT_DIR + "\\code\\tushare\\code.json"
    print(codes_path)
    if os.path.exists(codes_path):
        return read_json(codes_path)

    pro = ts.pro_api(TUSHARE_TOKEN)
    stock_df = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')

    # 筛选股票数据，上证和深证股票代码在sh.600000与sz.39900之间
    # stock_df = stock_df[(stock_df['code'] >= 'sh.600000') & (stock_df['code'] < 'sz.399000')]
    codes = stock_df['ts_code'].tolist()
    write_json(DATA_ROOT_DIR + "\\tushare\\code", 'code.json', codes)
    # 返回股票列表
    return codes


def get_stock_codes_from_baostock(date=None):
    codes_path = DATA_ROOT_DIR + "\\code\\baostock\\code.json"
    if os.path.exists(codes_path):
        return read_json(codes_path)
        # 登录baostock
    bs.login()

    # 从BaoStock查询股票数据
    stock_df = bs.query_all_stock(date).get_data()

    # 如果获取数据长度为0，表示日期date非交易日
    if 0 == len(stock_df):

        # 如果设置了参数date，则打印信息提示date为非交易日
        if date is not None:
            print('当前选择日期为非交易日或尚无交易数据，请设置date为历史某交易日日期')
            sys.exit(0)

        # 未设置参数date，则向历史查找最近的交易日，当获取股票数据长度非0时，即找到最近交易日
        delta = 1
        while 0 == len(stock_df):
            stock_df = bs.query_all_stock(datetime.date.today() - datetime.timedelta(days=delta)).get_data()
            delta += 1

    # 注销登录
    bs.logout()

    # 筛选股票数据，上证和深证股票代码在sh.600000与sz.39900之间
    stock_df = stock_df[(stock_df['code'] >= 'sh.600000') & (stock_df['code'] < 'sz.399000')]
    codes = stock_df['code'].tolist()
    write_json(DATA_ROOT_DIR + "\\code\\baostock", 'code.json', codes)
    # 返回股票列表
    return codes


def download_k_lines_from_baostock(stock_codes, frequency='d', from_date='1990-12-19',
                                   to_date=None,
                                   adjustflag='3'):
    """
    下载指定日期内，指定股票的日线数据

    :param frequency: 数据时间级别
    :param stock_codes: 待下载数据的股票代码
    :param from_date: 日线开始日期
    :param to_date: 日线结束日期
    :param adjustflag: 复权选项 1：后复权  2：前复权  3：不复权  默认为前复权
    :return: None
    """

    if to_date is None:
        to_date = _add_time(datetime.date.today(), days=-1).strftime('%Y-%m-%d')

    query_start = from_date

    # 下载股票循环
    for code in stock_codes:
        data_path = get_stock_path(stock_code=code, frequency=frequency, resource='baostock')
        if os.path.exists(data_path):
            df = pandas.read_csv(data_path).filter(items=['time'])
            latest_time = df.values[-1][0]

            query_start = _add_time(datetime.datetime.strptime(latest_time, '%Y-%m-%d %H:%M:%S'), 1)
            if query_start.timestamp() >= datetime.datetime.strptime(
                    to_date, '%Y-%m-%d').timestamp():
                return
            query_start = query_start.strftime('%Y-%m-%d')
        print(f'正在下载 {code}-{frequency}股票数据...')
        data_list = list()
        index_dict = {}
        index_names = []
        if frequency == 'd':
            # 如果是日线获取指数数据
            codes = code.split('.')
            # ts_code = codes[1] + "." + codes[0].title()
            # 获取指数数据 指数名称 未完成
            # index_dict, index_names = get_stock_index_from_tu_share(stock_code=ts_code)

        while True:
            bs.login()
            # 数据保存的位置
            save_path = get_stock_path(code, frequency)

            # 下载日线数据
            if frequency == 'd':
                out_df = bs.query_history_k_data_plus(code,
                                                      BAOSTOCK_DAY_FIELDS,
                                                      start_date=query_start, end_date=to_date,
                                                      frequency=frequency, adjustflag=adjustflag)
            # 下载分钟级别的数据
            else:
                out_df = bs.query_history_k_data_plus(code,
                                                      BAOSTOCK_MINUTE_FIELDS,
                                                      start_date=query_start, end_date=to_date,
                                                      frequency=frequency, adjustflag=adjustflag)
            # 注销登录
            bs.logout()
            # 解析数据
            while (out_df.error_code == '0') & out_df.next():
                row = out_df.get_row_data()
                fmt = '%Y-%m-%d'
                d = datetime.datetime.strptime(row[0], fmt)
                fmt = '%Y-%m-%d %H:%M:%S'
                row[0] = d.strftime(fmt)

                # 数据时间格式进行转换格式进行
                if frequency != 'd':
                    row = out_df.get_row_data()
                    fmt = '%Y%m%d%H%M%S'
                    t = datetime.datetime.strptime(row[1][:-3], fmt)
                    fmt = '%Y-%m-%d %H:%M:%S'
                    row[1] = t.strftime(fmt)
                    row[0] = t.strftime(fmt)

                else:
                    row.append(row[0])
                    # 指数数据
                    if row[0] in index_dict:
                        index = index_dict[row[0]]
                        # 添加指数数据
                        for i in index:
                            row.append(i)
                    else:
                        for i in range(len(index_names)):
                            row.append(0)
                # 获取一条记录，将记录合并在一起
                data_list.append(row)
            csv_head = out_df.fields
            if frequency == 'd':
                csv_head.append('time')

            end_date = data_list[-1][0]

            if _str2timestamp(end_date) >= _str2timestamp(to_date, '%Y-%m-%d'):
                break
            query_start = _timestamp2str(_str2timestamp(end_date) + FREQUENCY_SECOND[frequency], '%Y-%m-%d')

        result = pd.DataFrame(data_list, columns=csv_head)
        # 保存数据
        try:
            result.to_csv(save_path, index=False, mode='a')
            print(save_path)
        except OSError as r:
            print("OSError", r)
            os.makedirs(DATA_ROOT_DIR + f"\\baostock\\{frequency}")
            result.to_csv(save_path, index=False, mode='a')


# 不同时间级别对应的秒数
FREQUENCY_SECOND = {
    "1": 60,
    "5": 300,
    "15": 900,
    "30": 1800,
    "60": 3600,
    "d": 86400,
}


def _add_time(date, minutes=0, hour=0, days=0):
    date = date + datetime.timedelta(minutes=minutes, hours=hour, days=days)
    return date


def _timestamp2str(timestamp, fmt="%Y-%m-%d %H:%M:%S"):
    time_array = time.localtime(timestamp)
    return time.strftime(fmt, time_array)


def _str2timestamp(date: str, fmt="%Y-%m-%d %H:%M:%S"):
    """
    时间戳转字符串
    :param fmt:
    :param date:
    :return:
    """
    time_array = time.strptime(date, fmt)
    timestamp = int(time.mktime(time_array))
    return timestamp


def update_date(stocks=None, frequencys=None):
    """
    # 待完成
    更新本地股票数据
    :param stocks:
    :param frequencys: 更新的时间级别
    :return:
    """
    if stocks is None:
        stocks = get_stock_codes()
    # 获取所有股票的代码
    if frequencys is None:
        frequencys = ['d', '60', '30', '15', '5']

    for stock_code in stocks:
        for frequency in frequencys:
            download_k_lines_from_baostock([stock_code], frequency=frequency)


def _load_generic_csv_data(stock_code: str, frequency: str, start_time=datetime.datetime(2021, 1, 1),
                           end_time=datetime.datetime.now(), dformat='%Y-%m-%d %H:%M:%S'):
    """
    按照generic的格式加载数据

    :return:
    """

    timeframe = get_timeframe(frequency)

    # 文件名称
    file_path = get_stock_path(stock_code, frequency)
    df = pd.read_csv(
        file_path,
        skiprows=0,  # 不忽略行
        header=0,  # 列头在0行
    )
    return bt.feeds.GenericCSVData(
        dataname=file_path,
        nullvalue=0.0,
        fromdate=start_time,
        todate=end_time,
        dtformat=dformat,
        timeframe=timeframe,
        datetime=get_columns_index(df, 'time'),
        high=get_columns_index(df, 'high'),
        low=get_columns_index(df, 'low'),
        open=get_columns_index(df, 'open'),
        close=get_columns_index(df, 'close'),
        volume=get_columns_index(df, 'volume'),
        openinterest=-1
    )


def load_generic_csv_data(stock_code: str, frequency: str, start_time=datetime.datetime(2021, 1, 1),
                          end_time=datetime.datetime.now(), dformat='%Y-%m-%d %H:%M:%S'):
    """
    按照generic的格式加载数据

    :return:
    """

    timeframe = get_timeframe(frequency)

    # 文件名称
    file_path = get_stock_path(stock_code, frequency)
    df = pd.read_csv(
        file_path,
        skiprows=0,  # 不忽略行
        header=0,  # 列头在0行
    )
    return bt.feeds.GenericCSVData(
        dataname=file_path,
        nullvalue=0.0,
        fromdate=start_time,
        todate=end_time,
        dtformat=dformat,
        timeframe=timeframe,
        datetime=get_columns_index(df, 'date'),
        high=get_columns_index(df, 'high'),
        low=get_columns_index(df, 'low'),
        open=get_columns_index(df, 'open'),
        close=get_columns_index(df, 'close'),
        volume=get_columns_index(df, 'volume'),
        openinterest=-1
    )


def load_local_csv_data(stock_code: str, frequency: str, start_time=datetime.datetime(2021, 1, 1),
                        end_time=datetime.datetime.now(), dformat='%Y-%m-%d %H:%M:%S', resource='bao_stock'):
    if resource == 'bao_stock':
        if frequency == 'd':
            return _load_bao_stock_day_generic_csv(stock_code, frequency, start_time, end_time, dformat)
        elif frequency in ['5', '15', '30']:
            return _load_bao_stock_minute_generic_csv(stock_code, frequency, start_time, end_time, dformat)
    else:
        return _load_generic_csv_data(stock_code, frequency, start_time, end_time, dformat)


def get_timeframe(frequency: str):
    """
    获取时间级别
    :param frequency:
    :return:
    """
    timeframe = bt.TimeFrame.Days
    if frequency == 'd':
        timeframe = bt.TimeFrame.Days
    elif frequency in ['5', '15', '30']:
        timeframe = bt.TimeFrame.Minutes
    return timeframe


def _load_bao_stock_day_generic_csv(stock_code: str, frequency: str, start_time=datetime.datetime(2021, 1, 1),
                                    end_time=datetime.datetime.now(), dformat='%Y-%m-%d %H:%M:%S'):
    """
    按照generic的格式加载数据

    :return:
    """
    timeframe = get_timeframe(frequency)
    # 文件名称
    file_path = get_stock_path(stock_code, frequency)
    df = pd.read_csv(
        file_path,
        skiprows=0,  # 不忽略行
        header=0,  # 列头在0行
    )
    return cm.BaoStockDayGenericCSDataExtend(
        dataname=file_path,
        nullvalue=0.0,
        fromdate=start_time,
        todate=end_time,
        dtformat=dformat,
        timeframe=timeframe,
        datetime=get_columns_index(df, 'time'),
        high=get_columns_index(df, 'high'),
        low=get_columns_index(df, 'low'),
        open=get_columns_index(df, 'open'),
        close=get_columns_index(df, 'close'),
        volume=get_columns_index(df, 'volume'),
        amount=get_columns_index(df, 'amount'),
        adjustflag=get_columns_index(df, 'adjustflag'),
        turn=get_columns_index(df, 'turn'),
        tradestatus=get_columns_index(df, 'tradestatus'),
        pctChg=get_columns_index(df, 'pctChg'),
        isST=get_columns_index(df, 'isST'),

        openinterest=-1
    )


def _load_bao_stock_minute_generic_csv(stock_code: str, frequency: str, start_time=datetime.datetime(2021, 1, 1),
                                       end_time=datetime.datetime.now(), dformat='%Y-%m-%d %H:%M:%S'):
    """
    按照generic的格式加载数据

    :return:
    """
    timeframe = get_timeframe(frequency)
    # 文件名称
    file_path = get_stock_path(stock_code, frequency)
    df = pd.read_csv(
        file_path,
        skiprows=0,  # 不忽略行
        header=0,  # 列头在0行
    )
    print(get_columns_index(df, 'time'), )
    return cm.BaoStockMinuteGenericCSDataExtend(
        dataname=file_path,
        nullvalue=0.0,
        fromdate=start_time,
        todate=end_time,
        dtformat=dformat,
        timeframe=timeframe,
        datetime=get_columns_index(df, 'time'),
        high=get_columns_index(df, 'high'),
        low=get_columns_index(df, 'low'),
        open=get_columns_index(df, 'open'),
        close=get_columns_index(df, 'close'),
        volume=get_columns_index(df, 'volume'),
        amount=get_columns_index(df, 'amount'),
        adjustflag=get_columns_index(df, 'adjustflag'),

        openinterest=-1
    )


def get_columns_index(data, column_name):
    """
    获取表头所在位置
    :param data:
    :param column_name:
    :return:
    """
    index = 0
    for column in data.columns:
        if column == column_name:
            return index
        index += 1

    return -1

    pass


def get_stock_index_from_tu_share(stock_code='000001.SH', start_date=None, end_date=None):
    """
    获取股票的每日指数数据 (tushare仅仅提供少量的数据不完整。。。。待完成)
    :param end_date:
    :param start_date:
    :param stock_code: 000001.SH
    :return:
    """
    fmt = '%Y%m%d'
    days = -3000
    if end_date is None:
        end_date = datetime.datetime.now().strftime(fmt)
        start_date = _add_time(datetime.datetime.now(), days=-3000).strftime(fmt)
    stop_data = datetime.datetime.strptime('20040102', fmt).timestamp()
    index_dict = {}
    pro = ts.pro_api(TUSHARE_TOKEN)
    print(end_date, stop_data, start_date)

    while True:
        df = pro.index_dailybasic(fields=TUSHARE_INDEX_FIELDS, start_date=start_date, end_date=end_date,
                                  ts_code=stock_code)

        for index, row in df.iterrows():
            trade_date = datetime.datetime.strptime(row['trade_date'], fmt)
            trade_date = trade_date.strftime('%Y-%m-%d %H:%M:%S')
            index_dict[trade_date] = row.values
            print(row.values)

        days = days + days
        end_date = start_date
        start_date = _add_time(datetime.datetime.now(), days=days).strftime(fmt)
        if datetime.datetime.strptime(end_date, fmt).timestamp() <= stop_data:
            break

    return index_dict, TUSHARE_INDEX_FIELDS.split(",")


if __name__ == '__main__':
    update_date(frequencys=['d'])
