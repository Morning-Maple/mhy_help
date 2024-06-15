"""
图像对比类
"""

import json
import sys
import time
from enum import Enum

import cv2
import numpy as np
import onnxruntime as ort
import pygetwindow as gw
import pyautogui as pg
import torch
from ultralytics import YOLO

from HSR_Help.auto_daily.newTypes import Types


# def target_prediction(screen):
#     """模型预测
#     图片进行预测，并且返回预测结果和目标中心点
#     """
#     model_path = "../model/best.onnx"
#     ort_session = ort.InferenceSession(model_path)
#
#     screen = np.array(screen)
#     screen = cv2.cvtColor(screen, cv2.COLOR_BGR2RGB)
#     screen = cv2.resize(screen, (640, 640))
#     screen_data = np.array(screen) / 255.0
#     screen_data = np.transpose(screen_data, (2, 0, 1))
#     screen_data = np.expand_dims(screen_data, axis=0).astype(np.float32)
#
#     input_data = {ort_session.get_inputs()[0].name: screen_data}
#
#     output_data = ort_session.run(None, input_data)
#
#     print(output_data)
#     # 处理输出数据
#     for output in output_data:
#         print(output)

def center(center_list: list):
    """计算两组坐标的中心位置
    传入一个列表，期望只有四个元素，计算结果取四舍五入
    Args:
        center_list: 坐标列表
    Returns:
        tuple: 计算过后的中心位置
    Examples:
        >>> lists = [16, 21 , 54 , 98]
        >>> center(lists)
        (35, 60)
    """
    x_center = (center_list[0] + center_list[2]) / 2
    y_center = (center_list[1] + center_list[3]) / 2
    return round(x_center), round(y_center)


class ImagePositioning:
    _instance = None
    _model = None
    _verbose = True

    def __init__(self, mode=True):
        """
        Args:
            mode(bool): 是否输出测试日志，线上版本请置为False
        """
        self._model = YOLO("../model/best.pt")
        self._verbose = mode

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = object.__new__(cls)
        return cls._instance

    def target_prediction(self, screen: cv2.Mat, target: Types, threshold=None, can_zero=False, is_one=True):
        """获取单个目标的中心位置
        获取单个目标在图片的中心位置
        Args:
            screen: 待检测的图像
            target: 感兴趣的目标
            threshold: 阈值，不填则默认不使用阈值
            can_zero: 检测为0是否需要抛出移除
            is_one: 是否为单个目标(单目标存在多个且均可被选，请置为True)
        Returns:
            tuple: 目标置信度和在图片的位置，如果查询为0且can_zero为True，则返回0(置信度)和None(位置)
        Raise:
            ValueError: targe值不合法，检测的对象过多，检测对象为0
        """
        if target is None:
            raise ValueError('不合法的目标值')
        results = self._model.predict(screen, half=True, classes=[target.get_number], verbose=self._verbose)

        # 不设默认阈值，直接YOLO直出
        if threshold is None:
            threshold = 0
        # 有查询到结果，走这
        if len(results[0].boxes) != 0:
            # 单目标且仅有一个
            if len(results[0].boxes) == 1:
                if results[0].boxes[0].conf[0].item() >= threshold:
                    return results[0].boxes[0].conf[0].item(), center(results[0].boxes[0].xyxy[0].tolist())
                elif can_zero is True:
                    return 0, None
            # 单目标但是有多个，返回第一个找到的即可
            elif len(results[0].boxes) > 1 and is_one is False:
                if results[0].boxes[0].conf[0].item() >= threshold:
                    return results[0].boxes[0].conf[0].item(), center(results[0].boxes[0].xyxy[0].tolist())
                elif can_zero is True:
                    return 0, None
            else:
                raise ValueError('检测到多个可匹配对象，但是处于单目标模式，无法做出选择')
        # 查询不到结果，判断是否可以查询为0
        else:
            if can_zero:
                return 0, None
            else:
                raise ValueError(f'{threshold}置信度下匹配不到{target}目标')

    def target_prediction_one_to_many(
            self, screen: cv2.Mat,
            target_a: Types,
            target_b: Types,
            target_c: Types,
            threshold=0.7,
            can_zero_a=False,
            can_zero_b=False
    ):
        """返回离a最近的b或者c的位置
        通常a只找到一个(如果找不到a，直接返回)，b找到多个，c可能没有，然后计算离a最近的b和c，若离最近的是b，返回坐标，若是c，则抛出指定异常
        Args:
            screen: 待检测的图像
            target_a: 目标a(预期有且只有一个)
            target_b: 目标b(预期至少有一个)
            target_c: 目标c(预期可能没有，可能有多个)
            threshold: 检测阈值
            can_zero_a: 目标a是否能接受0个检测结果
            can_zero_b: 目标b是否能接受0个检测结果
        Returns:
            tuple: 离a最近的b的坐标
        Raises:
            ValueError: can_zero_a和can_zero_b为False时，还找不到目标a或者b
            RuntimeError: 离a最近的是目标c
        Examples:
            # 例如一个页面有多个传送按钮b，和可能存在追踪按钮c，要找到离a最近的传送按钮位置并返回，如果是追踪按钮c最近，说明目标a的传送点没开！
        """
        if target_a is None or target_b is None or target_c is None:
            raise ValueError('错误的传参')
        results = self._model.predict(screen,
                                      half=True,
                                      classes=[target_a.get_number, target_b.get_number, target_c.get_number],
                                      verbose=self._verbose
                                      )

        y_a = []
        y_b = []
        y_c = []
        # 解析所有感兴趣的对象，然后分别存储以用于后期预处理
        for result in results:
            for box in result.boxes:
                if box.cls[0].item() == target_a.get_number and box.conf[0].item() >= threshold:
                    x, y = center(box.xyxy[0].tolist())
                    y_a.append((x, y, box.id))
                elif box.cls[0].item() == target_b.get_number and box.conf[0].item() >= threshold:
                    x, y = center(box.xyxy[0].tolist())
                    y_b.append((x, y, box.id))
                elif box.cls[0].item() == target_c.get_number and box.conf[0].item() >= threshold:
                    x, y = center(box.xyxy[0].tolist())
                    y_c.append((x, y, box.id))

        if len(y_a) == 0:
            if can_zero_a is True:
                return 0, 0
            else:
                raise ValueError(f'检测不到目标：{target_a.get_desc_zn}')
        elif len(y_a) > 1:
            raise ValueError(f'目标：{target_a.get_desc_zn} 找到多个，无法确定')

        # 计算离目标a最近的目标b的位置
        if len(y_b) == 0:
            if can_zero_b is True:
                return None, 0
            else:
                raise ValueError(f'没有找到任何目标：{target_b.get_desc_zn}')

        y_res_bc = y_b + y_c
        min_diff = None
        min_diff_number = None
        closest_center: tuple = (0, 0)
        for loc in y_res_bc:
            x, y, names = loc
            diff = abs(y - y_a[0][1])
            if min_diff is None or diff < min_diff:
                min_diff = diff
                min_diff_number = names
                closest_center = x, y

        if min_diff_number == target_c.get_number:
            raise RuntimeError(f'目标{target_a.get_desc_zn} 的传送点没开，因为检测到了：{target_c.get_desc_zn} 按钮')

        return closest_center


if __name__ == "__main__":
    # img = cv2.imread('testt.png')
    # print(target_prediction(img))
    sys.exit()
