"""
图像对比类
"""

import json
import time
from enum import Enum

import cv2
import numpy as np

with open('config/default_config.json', 'r', encoding='utf-8') as f:
    config_default = json.load(f)


class ImageOperation(Enum):
    GRAY = 0
    """
    灰度
    """
    CANNY = 1
    """
    边缘
    """
    THRESHOLD = 2
    """
    二值化
    """


def get_variance(a, b):
    """
    计算两个图片的灰度值方差（必须同尺寸）
    Args:
        a: 目标图片1
        b: 目标图片2
    Returns:
        两张图片的接近程度（灰度值方差）
    """
    if a.shape != b.shape or a.ndim != b.ndim:
        raise IOError("图片尺寸不正确")

    variance_a = []
    variance_b = []
    sum_a = 0
    sum_b = 0
    sum_variance = 0.0

    for i in range(a.shape[0]):
        mean_a = np.mean(a[i])
        mean_b = np.mean(b[i])
        sum_a += mean_a
        sum_b += mean_b
        variance_a.append(mean_a)
        variance_b.append(mean_b)

    mean_a = sum_a / len(variance_a)
    mean_b = sum_b / len(variance_b)

    for i in range(len(variance_a)):
        var_a = (variance_a[i] - mean_a) ** 2
        var_b = (variance_b[i] - mean_b) ** 2
        sum_variance += abs(var_a - var_b)

    return sum_variance


def image_contrast(template_src, screen, is_show_detail=False):
    """
    图片匹配
    Args:
        template_src: 模板图片地址
        screen: 窗口截图
        is_show_detail: 是否展示匹配的详细信息
    Returns:
        tuple: 一个包含了最佳区域中心位置（x，y，最佳匹配度）的元组
    """
    global config_default

    template_image = cv2.imread(template_src, cv2.IMREAD_GRAYSCALE)
    if screen is None or template_image is None:
        raise IOError('无法加载图片')

    try:
        handle_screen = extra_handle_image(ImageOperation.GRAY, screen)
    except Exception as e:
        raise e
    handle_template_image = cv2.cvtColor(template_image, cv2.COLOR_BGR2GRAY)

    arr = {}
    for index in range(config_default["circulateRound"]):
        scale_percent = 1 - index * config_default["zoomRate"]
        temp_template = cv2.resize(handle_screen, None, fx=scale_percent, fy=scale_percent)

        result = cv2.matchTemplate(temp_template, handle_template_image, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)

        rect = (max_loc[0], max_loc[1], handle_template_image.shape[1], handle_template_image.shape[0])
        result_img_roi = temp_template[max_loc[1]:max_loc[1] + handle_template_image.shape[0],
                         max_loc[0]:max_loc[0] + handle_template_image.shape[1]]

        try:
            variance_diff = get_variance(result_img_roi, handle_template_image)
        except IOError as ioe:
            raise ioe

        arr[variance_diff] = (rect, temp_template, max_val)

    best_variance_diff = min(arr.keys())
    best_rect, best_mat, best_val = arr[best_variance_diff]

    center_x = best_rect[0] + best_rect[2] // 2
    center_y = best_rect[1] + best_rect[3] // 2

    # 在目标位置打框并返回
    if is_show_detail:
        print(f'{time.strftime("%Y%m%d-%H%M%S", time.localtime())} ：最大匹配度为：{best_val}')

        cv2.rectangle(best_mat, (best_rect[0], best_rect[1]),
                      (best_rect[0] + best_rect[2], best_rect[1] + best_rect[3]),
                      (255, 0, 0), 3)

        cv2.imshow("result", best_mat)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    return center_x, center_y, best_val


def extra_handle_image(method: ImageOperation, screen, CANNY_threshold1=100, CANNY_threshold2=200,
                       THRESHOLD_threshold_value=127, THRESHOLD_max_value=255):
    """
    对图片进行更多处理（灰度，边缘等）
    Args:
        method: 处理方法
        screen: 模板图片
        CANNY_threshold1: CANNY下阈值1
        CANNY_threshold2: CANNY下阈值2
        THRESHOLD_threshold_value: THRESHOLD下用于分割像素的阈值
        THRESHOLD_max_value: 高于阈值的像素所设置的值
    Returns:
        处理后的图片
    """
    try:
        match method:
            case ImageOperation.GRAY, _:
                screen = np.array(screen)
                screen = cv2.cvtColor(screen, cv2.COLOR_RGB2BGR)
                return cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)

            case ImageOperation.CANNY:
                return cv2.Canny(screen, CANNY_threshold1, CANNY_threshold2)

            case ImageOperation.THRESHOLD:
                _, screen = cv2.threshold(screen, THRESHOLD_threshold_value, THRESHOLD_max_value, cv2.THRESH_BINARY)
                return screen
    except Exception as e:
        return e
