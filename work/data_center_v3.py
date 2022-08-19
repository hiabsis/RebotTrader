import baostock as bs
import datetime
import sys
import numpy as np
import pandas as pd

# 可用日线数量约束
g_available_days_limit = 250

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
    下载指定日期内，指定股票的日线数据，计算扩展因子

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

        # 如果数据为空，则不创建
        if not out_df.shape[0]:
            continue

        # 删除重复数据
        out_df.drop_duplicates(['date'], inplace=True)

        # 日线数据少于g_available_days_limit，则不创建
        if out_df.shape[0] < g_available_days_limit:
            continue

        # 将数值数据转为float型，便于后续处理
        convert_list = ['open', 'high', 'low', 'close', 'preclose', 'volume', 'amount', 'turn', 'pctChg']
        out_df[convert_list] = out_df[convert_list].astype(float)

        # 重置索引
        out_df.reset_index(drop=True, inplace=True)

        # 计算扩展因子
        out_df = extend_factor(out_df)

        print(out_df)


def extend_factor(df):
    """
    计算扩展因子

    :param df: 待计算扩展因子的DataFrame
    :return: 包含扩展因子的DataFrame
    """

    # 使用pipe计算扩展因子
    df = df.pipe(zt).pipe(ss, delta_days=30)

    return df


def zt(df):
    """
    计算涨停因子

    若涨停，则因子为True，否则为False
    以当日收盘价较前一日收盘价上涨9.8%及以上作为涨停判断标准

    :param df: 待计算扩展因子的DataFrame
    :return: 包含扩展因子的DataFrame
    """

    df['zt'] = np.where((df['close'].values >= 1.098 * df['preclose'].values), True, False)

    return df


def shift_i(df, factor_list, i, fill_value=0, suffix='a'):
    """
    计算移动因子，用于获取前i日或者后i日的因子

    :param df: 待计算扩展因子的DataFrame
    :param factor_list: 待移动的因子列表
    :param i: 移动的步数
    :param fill_value: 用于填充NA的值，默认为0
    :param suffix: 值为a(ago)时表示移动获得历史数据，用于计算指标；值为l(later)时表示获得未来数据，用于计算收益
    :return: 包含扩展因子的DataFrame
    """

    # 选取需要shift的列构成新的DataFrame，进行shift操作
    shift_df = df[factor_list].shift(i, fill_value=fill_value)

    # 对新的DataFrame列进行重命名
    shift_df.rename(columns={x: '{}_{}{}'.format(x, i, suffix) for x in factor_list}, inplace=True)

    # 将重命名后的DataFrame合并到原始DataFrame中
    df = pd.concat([df, shift_df], axis=1)

    return df


def shift_till_n(df, factor_list, n, fill_value=0, suffix='a'):
    """
    计算范围移动因子

    用于获取前/后n日内的相关因子，内部调用了shift_i

    :param df: 待计算扩展因子的DataFrame
    :param factor_list: 待移动的因子列表
    :param n: 移动的步数范围
    :param fill_value: 用于填充NA的值，默认为0
    :param suffix: 值为a(ago)时表示移动获得历史数据，用于计算指标；值为l(later)时表示获得未来数据，用于计算收益
    :return: 包含扩展因子的DataFrame
    """

    for i in range(n):
        df = shift_i(df, factor_list, i + 1, fill_value, suffix)
    return df


def ss(df, delta_days=30):
    """
    计算双神因子，即间隔的两个涨停

    若当日形成双神，则因子为True，否则为False

    :param df: 待计算扩展因子的DataFrame
    :param delta_days: 两根涨停间隔的时间不能超过该值，否则不判定为双神，默认值为30
    :return: 包含扩展因子的DataFrame
    """

    # 移动涨停因子，求取近delta_days天内的涨停情况，保存在一个临时DataFrame中
    temp_df = shift_till_n(df, ['zt'], delta_days, fill_value=False)

    # 生成列表，用于后续检索第2天前至第delta_days天前是否有涨停出现
    col_list = ['zt_{}a'.format(x) for x in range(2, delta_days + 1)]

    # 计算双神，需同时满足3个条件：
    # 1、第2天前至第delta_days天前，至少有1个涨停
    # 2、1天前不是涨停（否则就是连续涨停，不是间隔的涨停）
    # 3、当天是涨停
    df['ss'] = temp_df[col_list].any(axis=1) & ~temp_df['zt_1a'] & temp_df['zt']

    return df


if __name__ == '__main__':
    stock_codes = get_stock_codes()
    create_data(stock_codes)
