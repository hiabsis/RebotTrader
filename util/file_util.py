import csv

import setting
import imgkit
import os
from setting import wk_img_path
from PIL import Image
from time import strftime, localtime
from util import string_util


def print_time():
    print(strftime("%Y-%m-%d %H:%M:%S", localtime()))
    return


def get_size(file):
    """
    获取文件大小:KB
    :param file:
    :return:
    """
    size = os.path.getsize(file)
    return size / 1024


def get_outfile(infile, outfile):
    if outfile:
        return outfile
    dir, suffix = os.path.splitext(infile)
    outfile = '{}_compress{}'.format(dir, suffix)
    return outfile


def compress_image(infile, outfile=None, mb=150, step=10, quality=80):
    """ 压缩图片
    :param infile: 压缩源文件
    :param outfile: 压缩文件保存地址
    :param mb: 压缩目标，KB
    :param step: 每次调整的压缩比率
    :param quality: 初始压缩比率
    :return: 压缩文件地址，压缩文件大小
    """
    o_size = get_size(infile)
    if o_size <= mb:
        return infile
    outfile = get_outfile(infile, outfile)
    while o_size > mb:
        im = Image.open(infile)
        im.save(outfile, quality=quality)
        if quality - step < 0:
            break
        quality -= step
        o_size = get_size(outfile)

    return outfile, get_size(outfile)


def html2img(html: str, output=None):
    """
      把静态网页保存为图片
      :param html: 文件路径
      :param output: 保存位置
      :return: 保存后的图片位置
    """
    cfg = imgkit.config(wkhtmltoimage=wk_img_path)

    if output is None:
        output = setting.image_root_path + string_util.generate_random_str(6) + ".png"
    print(output)
    imgkit.from_file(html, output, config=cfg)

    return output


def date2csv(data, file_name, head, write_type=None):
    """
    数据保存为csv
    :param write_type: 写入数据类型 a 添加 w 覆盖写
    :param data: 数据
    :param file_name: 文件名称
    :param head: 表头
    :return: 文件保存路径
    """
    if write_type is None:
        write_type = 'w'
    file_path = setting.date_root_path + "\\" + file_name + ".csv"
    with open(file_path, write_type) as csvfile:
        writer = csv.writer(csvfile, lineterminator='\n')
        writer.writerow(head)
        writer.writerows(data)
    return file_path
