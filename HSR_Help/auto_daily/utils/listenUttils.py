import time

import keyboard


def use_key_in_time(key, count, time_limit):
    """
    监听键盘事件，在规定时间内按下指定键指定次数，返回True，超时返回False
    Args:
        key: 监听的键名
        count: 指定按键次数
        time_limit: 规定时间（秒）
    Returns:
        bool: 是否在规定时间内按下指定键指定次数
    """
    start_time = time.time()
    key_count = 0
    while True:
        if keyboard.is_pressed(key):
            key_count += 1
            if key_count == count:
                return True
        if time.time() - start_time > time_limit:
            return False


def hold_key_in_time(key, hold_time, time_limit):
    """
    监听键盘事件，检测按下某个键超过指定时间，返回True，超时返回False
    Args:
        key: 监听的键名
        hold_time: 指定按键保持时间（秒）
        time_limit: 规定时间（秒）
    Returns:
        bool: 是否在规定时间内按下指定键超过指定时间
    """
    start_time = time.time()
    while True:
        if keyboard.is_pressed(key):
            key_start_time = time.time()
            while keyboard.is_pressed(key):
                if time.time() - key_start_time >= hold_time:
                    return True
                if time.time() - start_time > time_limit:
                    return False
        if time.time() - start_time > time_limit:
            return False
