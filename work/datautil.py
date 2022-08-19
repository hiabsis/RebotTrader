import baostock as bs
import datetime
import sys


def get_stock_codes(date=None):
    """
    获取指定日期的A股代码列表

    若参数date为空，则返回最近1个交易日的A股代码列表
    若参数date不为空，且为交易日，则返回date当日的A股代码列表
    若参数date不为空，但不为交易日，则打印提示非交易日信息，程序退出

    :param date: 日期
    :return: A股代码的列表
    """

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
            print(stock_df)
            delta += 1

    # 注销登录
    bs.logout()

    # 筛选股票数据，上证和深证股票代码在sh.600000与sz.39900之间
    stock_df = stock_df[(stock_df['code'] >= 'sh.600000') & (stock_df['code'] < 'sz.399000')]

    # 返回股票列表
    return stock_df['code'].tolist()


import baostock as bs
import datetime
import sys

# BaoStock日线数据字段
g_baostock_data_fields = 'date,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,peTTM,pbMRQ, psTTM,pcfNcfTTM,isST'


def get_stock_codes(date=None):
    """
    获取指定日期的A股代码列表

    若参数date为空，则返回最近1个交易日的A股代码列表
    若参数date不为空，且为交易日，则返回date当日的A股代码列表
    若参数date不为空，但不为交易日，则打印提示非交易日信息，程序退出

    :param date: 日期
    :return: A股代码的列表
    """

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

    # 返回股票列表
    return stock_df['code'].tolist()


def create_data(stock_codes, from_date='1990-12-19', to_date=datetime.date.today().strftime('%Y-%m-%d'),
                adjustflag='2'):
    """
    下载指定日期内，指定股票的日线数据

    :param stock_codes: 待下载数据的股票代码
    :param from_date: 日线开始日期
    :param to_date: 日线结束日期
    :param adjustflag: 复权选项 1：后复权  2：前复权  3：不复权  默认为前复权
    :return: None
    """

    # 下载股票循环
    for code in stock_codes:
        print('正在下载{}...'.format(code))

        # 登录BaoStock
        bs.login()

        # 下载日线数据
        out_df = bs.query_history_k_data_plus(code, g_baostock_data_fields, start_date=from_date, end_date=to_date,
                                              frequency='d', adjustflag=adjustflag).get_data()

        # 注销登录
        bs.logout()

        # 剔除停盘数据
        if out_df.shape[0]:
            out_df = out_df[(out_df['volume'] != '0') & (out_df['volume'] != '')]
        # 剔除ST数据
        # 流通量
        print(out_df)


if __name__ == '__main__':
    stock_codes = get_stock_codes()
    create_data(stock_codes)

# if __name__ == '__main__':
#     stock_codes = get_stock_codes()
#     print(stock_codes)
#     print(len(stock_codes))
