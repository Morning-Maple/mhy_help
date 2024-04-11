import logging
import os
from datetime import datetime
from enum import Enum


class LoggerLevel(Enum):
    DEBUG = 'DEBUG级别输出'
    INFO = 'INFO级别输出'
    WARNING = 'WARNING级别输出'
    ERROR = 'ERROR级别输出'
    CRITICAL = 'CRITICAL级别输出'


def setup_logging():
    # 创建 logs 文件夹，如果不存在
    os.makedirs('logs', exist_ok=True)

    current_date = datetime.now().strftime('%Y%m%d')

    # 配置
    logging.basicConfig(
        level=logging.INFO,
        encoding='utf-8',
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        filename=f'logs/log_{current_date}.log',
        filemode='a'  # 追加模式
    )

    # 如果需要在控制台同时输出日志，可以添加一个 StreamHandler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logging.getLogger().addHandler(console_handler)

    logging.getLogger().info('\n--------')
    logging.getLogger().info("NOOB PROJECT BY MORNING_MAPLE :|")
    logging.getLogger().info('>>>> 初始化完毕')
    return logging.getLogger()
