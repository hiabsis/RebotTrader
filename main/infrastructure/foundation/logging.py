import datetime
import logging
import os

import colorlog

from main.resource.config import LOG_LEVEL


class Logging(object):

    def log(self, level='INFO'):  # 生成日志的主方法,传入对那些级别及以上的日志进行处理

        log_colors_config = {
            'DEBUG': 'white',
            'INFO': 'white',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'bold_red',
        }

        logger = logging.getLogger()  # 创建日志器

        logger.setLevel(level)  # 设置日志级别

        root_path = os.getcwd()
        file_name = datetime.datetime.now().strftime('%Y%m%d_%H%M%S') + ".log"
        # log_path = os.path.join(root_path, self.log_path, file_name)

        if not logger.handlers:  # 作用,防止重新生成处理器
            sh = logging.StreamHandler()  # 创建控制台日志处理器
            # fh = logging.FileHandler(filename=log_path, mode='a', encoding="utf-8")  # 创建日志文件处理器
            # 创建格式器
            fmt = logging.Formatter(
                fmt='[%(asctime)s.%(msecs)03d] %(filename)s:%(lineno)d [%(levelname)s]: %(message)s',
                datefmt='%Y-%m-%d  %H:%M:%S')

            sh_fmt = colorlog.ColoredFormatter(
                fmt='%(log_color)s[%(asctime)s.%(msecs)03d] %(filename)s:%(lineno)d [%(levelname)s]: %(message)s',
                datefmt='%Y-%m-%d  %H:%M:%S',
                log_colors=log_colors_config)
            # 给处理器添加格式
            sh.setFormatter(fmt=sh_fmt)
            # fh.setFormatter(fmt=fmt)
            # 给日志器添加处理器，过滤器一般在工作中用的比较少，如果需要精确过滤，可以使用过滤器
            logger.addHandler(sh)
            # logger.addHandler(fh)
        return logger  # 返回日志器


log = Logging().log(level=LOG_LEVEL)


class LoggingFactory:

    @staticmethod
    def instance():
        return log

