import csv
import json

import os


class FileUtil:

    @staticmethod
    def data2csv(data, head, file_path: str, write_type=None):
        """
        数据保存为csv
        :param write_type: 写入数据类型 a 添加 w 覆盖写
        :param data: 数据
        :param file_path: 文件路径
        :param head: 表头
        :return: 文件保存路径
        """
        if write_type is None:
            write_type = 'w'
        if not os.path.exists(file_path):
            os.makedirs(file_path[0:len(file_path) - 4])

            with open(file_path, write_type) as csvfile:
                writer = csv.writer(csvfile, lineterminator='\n')
                writer.writerow(head)
        with open(file_path, write_type) as csvfile:
            writer = csv.writer(csvfile, lineterminator='\n')

            writer.writerows(data)
        return file_path

    @staticmethod
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

    @staticmethod
    def write_json(path, load_dict):
        """
        文件写入json
        :param path:
        :param load_dict:
        :return:
        """
        with open(path, 'w') as write_f:
            write_f.write(json.dumps(load_dict, indent=4, ensure_ascii=False))
