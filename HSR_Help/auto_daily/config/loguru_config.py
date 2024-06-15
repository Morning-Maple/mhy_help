import sys
from loguru import logger
from datetime import datetime
import os


def setup_logger(debug_mode=False):
    """
    全局日志配置
    """
    # 获取当前日期
    today = datetime.now().strftime('%Y%m%d')

    # 创建日志目录
    common_log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs', 'common')
    crash_log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs', 'crash')
    os.makedirs(common_log_dir, exist_ok=True)
    os.makedirs(crash_log_dir, exist_ok=True)

    # 配置控制台输出
    logger.remove()  # 移除默认的日志输出
    console_level = "DEBUG" if debug_mode else "INFO"
    logger.add(sys.stdout, level=console_level)

    # 配置文件输出（按天轮转，大小不超过16MB，多进程支持）
    common_log_file = os.path.join(common_log_dir, f"logs_{today}.log")
    common_log_format = "{time:YYYY-MM-DD HH:mm:ss} | {level} ：{message}\n"

    def handle_level(record):
        if record["level"].name == "INFO":
            return "{time:YYYY-MM-DD HH:mm:ss} | 信息：{message}\n"
        elif record["level"].name == "WARNING":
            return "{time:YYYY-MM-DD HH:mm:ss} | >异常<：{message}\n"
        return common_log_format

    logger.add(common_log_file,
               rotation="00:00",
               retention="15 days",
               compression=None,
               enqueue=True,
               filter=lambda record: record["level"].name in ["INFO", "WARNING"],
               level="INFO",
               format=handle_level
               )

    # 配置详细日志输出（按运行次轮转）
    crash_log_file = os.path.join(crash_log_dir, f"crash_{today}.log")
    logger.add(crash_log_file,
               rotation="00:00",
               retention="15 days",
               compression="zip",
               enqueue=True,
               level="DEBUG"
               )

    return logger
