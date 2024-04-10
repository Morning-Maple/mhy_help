import threading
import time
from enum import Enum

import cv2
import keyboard
import numpy as np
import pyautogui as pg


class ImageOperation(Enum):
    CANNY = "canny"
    THRESHOLD = "threshold"


def screenshot(regions, gray=True, is_show=False):
    """
    对目标区域进行截图
    Args:
        regions:  截图区域
        gray (bool): 是否进行灰度处理
        is_show (bool): 是否临时展示
    Returns:
        Image: 截图的图片
    """
    screen = pg.screenshot(region=regions)

    if is_show:
        screen.show()

    if gray:
        screen = np.array(screen)
        screen = cv2.cvtColor(screen, cv2.COLOR_RGB2BGR)
        screen = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
    return screen


def image_contrast(
        image,
        screen,
        expand: list[ImageOperation],
        threshold=0.9,
        method=cv2.TM_CCOEFF_NORMED,
        is_show_detail=False
):
    """
    点击目标图片（必须传入灰度图）
    Args:
        image (UMat): 模板图片
        screen (UMat): 截图
        expand (list[ImageOperation]): 图片的额外处理
        threshold (float): 阈值[0,1]（越高越精准）
        method (int): CV的处理方式
        is_show_detail (bool): 是否输出匹配详情（匹配情况和最大匹配值）
    Returns:
        bool: True如果点击成功，否则返回False
        tuple: 匹配到的模板的中心位置
    """
    if expand is None:
        expand = []

    # 额外处理
    for op in expand:
        if op == ImageOperation.CANNY:
            screen = cv2.Canny(screen, threshold1=100, threshold2=200)
            image = cv2.Canny(image, threshold1=100, threshold2=200)
        elif op == ImageOperation.THRESHOLD:
            _, screen = cv2.threshold(screen, 127, 255, cv2.THRESH_BINARY)
            _, image = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)

    res = cv2.matchTemplate(screen, image, method)
    _, max_val, _, max_loc = cv2.minMaxLoc(res)
    if max_val >= threshold:
        h, w = image.shape[:2]
        center_loc = (max_loc[0] + w // 2, max_loc[1] + h // 2)

        if is_show_detail:
            print(f'{time.strftime("%Y%m%d-%H%M%S", time.localtime())} ：匹配！最大匹配度为：{max_val}')

        return True, center_loc
    else:

        if is_show_detail:
            print(f'{time.strftime("%Y%m%d-%H%M%S", time.localtime())} ：不匹配！最大匹配度为：{max_val}')

        return False, None


def repeat_check(
        regions,
        expand: list[ImageOperation],
        image1=None,
        image2=None,
        rounds=1,
        sleep=0,
        threshold=0.9,
        method=cv2.TM_CCOEFF_NORMED,
        is_show_detail=False
):
    """
    重复检测
    Args:
        regions: 检测目标区域
        expand:  额外的处理方式，None和[]为不做额外处理
        image1:  模板1（成功会返回坐标）
        image2:  模板2（成功不会返回坐标）
        rounds:  重复次数
        sleep:   重复检测的延迟
        threshold: 阈值，大于等于才算匹配
        method: CV2方法，参考CV2.matchTemplate()的第三个参数
        is_show_detail: 是否展示检测详情（是否匹配，匹配度）
    Returns:
        bool: 匹配的结果
        tuple: 匹配的中心位置（基于regions）
    """
    if expand is None:
        expand = []

    b, loc = (False, None)
    b1, loc1 = (False, None)

    for _ in range(rounds):
        time.sleep(sleep)
        if image1 is not None:
            b, loc = image_contrast(image1, screenshot(regions), expand, threshold, method, is_show_detail)
        if image2 is not None:
            b1, loc1 = image_contrast(image2, screenshot(regions), expand, threshold, method, is_show_detail)

        if b:
            return b, loc
        elif b1:
            return True, None
        else:
            continue

    return b, loc


def listen_for_double_space(timeout=300, interval=2):
    """
    监听双空格键事件，如果在2秒内按下两次空格键或超过五分钟后返回True
    Args:
        timeout (int): 超时时间（秒）
        interval (int)： 规定时间内按下两次空格
    Returns:
        bool: 无论如何都返回True
    """

    start_time = time.time()
    space_count = 0

    def reset_space_count():
        nonlocal space_count
        space_count = 0

    def on_space(event):
        nonlocal space_count
        space_count += 1
        if space_count == 1:
            # 重置计数器的定时器
            threading.Timer(interval, reset_space_count).start()
        elif space_count == 2:
            # 按下两次空格键
            keyboard.unhook_all()
            return True

    keyboard.on_press_key("space", on_space)

    while time.time() - start_time < timeout:
        if space_count == 2:
            return True
        time.sleep(0.1)

    # 超时
    keyboard.unhook_all()
    return True
