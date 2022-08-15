import os
import sys
import time
import pandas as pd
from struct import unpack

# 获取当前目录
proj_path = os.path.dirname(os.path.abspath(sys.argv[0])) + '/../'


# 将通达信的日线文件转换成CSV格式
def day2csv(source_dir, file_name, target_dir):
    # 以二进制方式打开源文件
    source_file = open(source_dir + os.sep + file_name, 'rb')
    buf = source_file.read()
    source_file.close()

    # 打开目标文件，后缀名为CSV
    target_file = open(target_dir + os.sep + file_name[: file_name.rindex('.')] + '.csv', 'w')
    buf_size = len(buf)
    rec_count = int(buf_size / 32)
    begin = 0
    end = 32
    header = str('date') + ',' + str('open') + ',' + str('high') + ',' + str('low') + ',' \
             + str('close') + ',' + str('amount') + ',' + str('volume') + '\n'
    target_file.write(header)
    for i in range(rec_count):
        # 将字节流转换成Python数据格式
        # I: unsigned int
        # f: float
        a = unpack('IIIIIfII', buf[begin:end])
        # 处理date数据
        year = a[0] // 10000
        month = (a[0] % 10000) // 100
        day = (a[0] % 10000) % 100
        date = '{}-{:02d}-{:02d}'.format(year, month, day)

        line = date + ',' + str(a[1] / 100.0) + ',' + str(a[2] / 100.0) + ',' \
               + str(a[3] / 100.0) + ',' + str(a[4] / 100.0) + ',' + str(a[5]) + ',' \
               + str(a[6]) + '\n'
        target_file.write(line)
        begin += 32
        end += 32
    target_file.close()


def transform_data():
    # 保存csv文件的目录
    target = proj_path + 'data/tdx/day'
    if not os.path.exists(target):
        os.makedirs(target)
    code_list = []
    source_list = ['C:/new_tdx/vipdoc/sz/lday', 'C:/new_tdx/vipdoc/sh/lday']
    for source in source_list:
        file_list = os.listdir(source)
        # 逐个文件进行解析
        for f in file_list:
            day2csv(source, f, target)
        # 获取所有股票/指数代码
        code_list.extend(list(map(lambda x: x[:x.rindex('.')], file_list)))
    # 保存所有代码列表
    pd.DataFrame(data=code_list, columns=['code']).to_csv(proj_path + 'data/tdx/all_codes.csv', index=False)


def extract_data(from_date, file_name):
    # 以二进制方式打开源文件
    source_file = open(file_name, 'rb')
    buf = source_file.read()
    source_file.close()
    buf_size = len(buf)
    rec_count = int(buf_size / 32)
    # 从文件末开始访问数据
    begin = buf_size - 32
    end = buf_size
    data = []
    for i in range(rec_count):
        # 将字节流转换成Python数据格式
        # I: unsigned int
        # f: float
        a = unpack('IIIIIfII', buf[begin:end])
        # 处理date数据
        year = a[0] // 10000
        month = (a[0] % 10000) // 100
        day = (a[0] % 10000) % 100
        date = '{}-{:02d}-{:02d}'.format(year, month, day)
        if from_date == date:
            break
        data.append([date, str(a[1] / 100.0), str(a[2] / 100.0), str(a[3] / 100.0), \
                     str(a[4] / 100.0), str(a[5]), str(a[6])])
        begin -= 32
        end -= 32
    # 反转数据
    data.reverse()
    return data


def update_data():
    # 读入所有股票/指数代码
    codes = pd.read_csv(proj_path + 'data/tdx/all_codes.csv')['code']
    for code in codes:
        data_path = proj_path + 'data/tdx/day/' + code + '.csv'
        # 读取当前已存在的数据
        exist_df = pd.read_csv(data_path)
        # 获取需要更新的日线开始时间
        from_date = pd.read_csv(proj_path + 'data/tdx/day/' + code + '.csv')['date'].iloc[-1]
        # 提取新数据
        data = extract_data(from_date, 'C:/new_tdx/vipdoc/' + code[0:2] + '/lday/' + code + '.day')
        if not len(data):
            continue
        df = pd.DataFrame(data).rename(
            columns={0: 'date', 1: 'open', 2: 'high', 3: 'low', 4: 'close', 5: 'amount', 6: 'volume'})
        # 合并数据
        df = exist_df.append(df)
        # 保存文件
        df.to_csv(data_path, index=False)


def get_all_stock_codes():
    all_codes_file = proj_path + 'data/tdx/all_codes.csv'
    if not os.path.exists(all_codes_file):
        print('请先更新数据！')
        return
    df = pd.read_csv(all_codes_file)
    df = df[((df['code'] >= 'sh600000') & (df['code'] <= 'sh605999')) | \
            ((df['code'] >= 'sz000001') & (df['code'] <= 'sz003999')) | \
            ((df['code'] >= 'sz300000') & (df['code'] <= 'sz300999'))]
    df.to_csv(proj_path + 'data/tdx/all_stock_codes.csv', index=False)


if __name__ == '__main__':
    # 程序开始时的时间
    time_start = time.time()

    # 获取所有股票代码
    # get_all_stock_codes()

    # 转换所有数据
    transform_data()

    # 更新数据
    # update_data()

    # 程序结束时系统时间
    time_end = time.time()

    print('程序所耗时间：', time_end - time_start)
