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


# with open('config/default_config.json', 'r', encoding='utf-8') as f:
#     config_default = json.load(f)


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
    _model = None

    def __init__(self, path: str):
        self._model = YOLO(path)

    def target_prediction(self, screen: cv2.Mat, target: Types, threshold=0.7):
        """获取目标的中心位置
        获取目标在图片的中心位置，期望目标有且只有一个
        Args:
            screen: 待检测的图像
            target: 感兴趣的目标
            threshold: 阈值
        Returns:
            tuple: 感兴趣的目标在图片的位置
        Raise:
            ValueError: targe值不合法，检测的对象过多，检测对象为0
        """
        if target is None:
            raise ValueError('不合法的目标值')
        results = self._model.predict(screen, half=True, classes=[target.get_number])

        if len(results) == 1 and results[0].boxes.conf.item() >= threshold:
            return results[0].boxes.conf.item(), center(results[0].boxes.xyxy[0].tolist())
        if len(results) > 1:
            raise ValueError('检测到多个可匹配对象，但是不知道应该选哪个')
        else:
            raise ValueError(f'{threshold}置信度下匹配不到{target}目标')

    def target_prediction_one_to_many(self, screen: cv2.Mat, target_a: Types, target_b: Types, threshold=0.7):
        """返回离a最近的b的位置
        通常a只找到一个，b找到多个，然后计算离a最近的b，并且返回该b的坐标
        Args:
            screen: 待检测的图像
            target_a: 目标a(预期有且只有一个)
            target_b: 目标b(预期至少有一个)
            threshold: 检测阈值
        Returns:
            tuple: 离a最近的b的坐标
        Raises:
            ValueError: 找不到目标a或者b
        Examples:
            >>> # 非最终版例子
            >>> b = [(1, 3), (2, 8), (3, 15), (4, 6)]
            >>> a = 7
            >>> self.target_prediction_one_to_many(b, a)
            (4, 6)

            >>> b = [(1, 10), (2, 20), (3, 30)]
            >>> a = 25
            >>> self.target_prediction_one_to_many(b, a)
            (3, 30)
        """
        results = self._model.predict(screen, half=True, classes=[target_a.get_number, target_b.get_number])

        y_a = None
        y_b = []
        # 解析所有感兴趣的对象，然后分别存储以用于后期预处理
        for result in results:
            if result.names == target_a.name and result.boxes.conf.item() >= threshold:
                _, y_a = center(result.boxes.xyxy[0].tolist())
            elif result.names == target_b.name and result.boxes.conf.item() >= threshold:
                x, y = center(result.boxes.xyxy[0].tolist())
                y_b.append(y)

        if y_a is None:
            raise ValueError(f'检测不到目标：{target_a.get_desc_zn}')

        # 计算离目标a最近的目标b的位置
        min_diff = None
        closest_center: tuple = (0, 0)
        for loc in y_b:
            x, y = loc
            diff = abs(y - y_a)
            if min_diff is None:
                min_diff = diff
            elif diff < min_diff:
                min_diff = diff
                closest_center = (x, y)

        if closest_center == (0, 0):
            raise ValueError(f'找不到离目标：{target_a.get_desc_zn} 最近的：{target_b.get_desc_zn}')

        return closest_center


if __name__ == "__main__":
    # img = cv2.imread('testt.png')
    # print(target_prediction(img))
    sys.exit()
