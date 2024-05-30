import json
import time

import pygetwindow as gw
import pyautogui as pg
from config.loguru_config import setup_logger
from Types import ModeType
from utils.ScreenShot import ScreenShot
from utils.ImagePositioning import image_contrast


class DailyScript:
    _instance = None
    _auto_battle = False
    _double_speed = False
    _screen_shot: ScreenShot

    user_config = None
    logs = None

    w_left = 0
    w_top = 0
    w_width = 0
    w_height = 0
    region = (0, 0, 0, 0)

    def __init__(self, mode: bool):
        self.config_set()
        self.logs_set(mode)
        self.game_window_set()
        self._screen_shot = ScreenShot(self.region)

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = object.__new__(cls)
        return cls._instance

    def config_set(self):
        """
        设置配置文件
        """
        with open('config/new_config.json', 'r', encoding='utf-8') as f:
            self.user_config = json.load(f)

    def logs_set(self, mode: bool):
        """日志设定"""
        self.logs = setup_logger(mode)

    def r_o(self, x, y, w, h):
        """region_operation
            处理截图区域
        """
        return self.w_left + (x * self.w_width), self.w_top + (y * self.w_height), self.w_width * w, self.w_height * h

    def click(self, x, y, x_operation=0.0, y_operation=0.0):
        """鼠标点击事件"""
        pg.click(self.w_left + self.w_left * x_operation + x, self.w_top + self.w_top * y_operation + y)

    def game_window_set(self):
        """
        获取窗口区域大小
        """
        game_window = gw.getWindowsWithTitle('崩坏：星穹铁道')

        if not game_window.isActive:
            # 防止最小化，同时激活窗口
            game_window.restore()
            game_window.activate()

        if self.w_top != game_window.top:
            # 获取窗口的位置信息
            self.w_left, self.w_top, self.w_width, self.w_height = game_window.left, game_window.top, game_window.width, game_window.height
            self.region = (self.w_left, self.w_top, self.w_width, self.w_height)

    def run_script(self):
        """脚本运行"""
        time.sleep(0.5)
        pg.press('M')
        time.sleep(1.5)

        if self.user_config["project"]["weiTuo"] == 1:
            self.wei_tuo()

        if self.user_config["project"]["email"] == 1:
            self.email()

        if self.user_config["project"]["zhuZhan"] == 1:
            self.help_money()

        if self.user_config["project"]["fuBen"] == 1:
            self.fu_ben()

        if self.user_config["project"]["shiXun"] == 1:
            self.shi_xun()

        if self.user_config["project"]["xunLi"] == 1:
            self.xun_li()

    def wei_tuo(self):
        """委托派遣"""
        time.sleep(2)
        pg.press('ESC')
        time.sleep(2)

        screen = self._screen_shot.screenshot(self.r_o(0.67, 1, 0.33, 0.4))
        x, y, _ = image_contrast('image/button_weituo.png', screen)
        self.click(x, y, 0.67)
        time.sleep(1.5)

        # TODO 领取区域不确定
        screen = self._screen_shot.screenshot(self.r_o(0.5, 0.806, 0.37, 0.0926))
        x, y, match = image_contrast('image/button_one_click_get_1.png', screen)
        if match >= 0.9:
            self.click(x, y, 0.5)
            time.sleep(1.5)
        else:
            self.logs.info("无可领取的委托派遣！")
            pg.press('ESC')
            time.sleep(1.5)
            pg.press('ESC')
            return

        screen = self._screen_shot.screenshot(self.r_o(0.5, 0.806, 0.37, 0.0926))
        x, y, match = image_contrast('image/button_again_weituo.png', screen)
        self.click(x, y, 0.5, 0.806)
        self.logs.info("日常派遣已经领取且已重新派遣")
        time.sleep(3)

        pg.press('ESC')
        time.sleep(1.5)
        pg.press('ESC')

    def email(self):
        """邮件领取"""
        time.sleep(2)
        pg.press('ESC')
        time.sleep(1.5)

        screen = self._screen_shot.screenshot(self.r_o(0.67, 1, 0.33, 0.4))
        x, y, _ = image_contrast('image/button_email.png', screen)
        self.click(x, y, 0.67)
        time.sleep(1.5)

        screen = self._screen_shot.screenshot(self.r_o(1, 0.87, 0.13, 0.292))
        x, y, match = image_contrast('image/button_all_get.png', screen)
        if match >= 0.9:
            self.click(x, y, y_operation=0.87)
            time.sleep(1.5)
            pg.press('ESC')
            time.sleep(1)
        else:
            self.logs.info("无邮件可领取！")

        pg.press('ESC')
        time.sleep(1.5)
        pg.press('ESC')

    def help_money(self):
        """助战奖励"""
        time.sleep(2)
        pg.press('ESC')
        time.sleep(1.5)

        screen = self._screen_shot.screenshot(self.r_o(0.891, 1, 210, 130))
        x, y, _ = image_contrast('image/button_q.png', screen)
        self.click(x, y, 0.891)
        time.sleep(1.5)

        screen = self._screen_shot.screenshot(self.r_o(0.67, 1, 0.33, 0.4))
        x, y, _ = image_contrast('image/button_myqz.png', screen)
        self.click(x, y, 0.67)
        time.sleep(1.5)

        screen = self._screen_shot.screenshot(self.r_o(0.792, 1, 0.208, 0.278))
        x, y, match = image_contrast('image/button_get_q.png', screen)
        if match >= 0.9:
            self.click(x, y, y_operation=0.792)
            time.sleep(1.5)
            pg.press('ESC')
            time.sleep(1)
        else:
            self.logs.info("无邮件可领取！")

        pg.press('ESC')
        time.sleep(1.5)
        pg.press('ESC')

    def fu_ben(self):
        """
        副本挑战
        """
        pass

    def shi_xun(self):
        """实训领取"""
        pass

    def xun_li(self):
        """巡礼领取"""

        pass

    def choose_mode(self):
        """模式大类选择"""
        pass

    def choose_mode_detail(self):
        """模式小类选择"""
        pass

    def enter_mode(self):
        """进入挑战"""
        time.sleep(4)
        self.click(290, 40, 0.698, 0.874)
        time.sleep(2)
        self.click(290, 40, 0.698, 0.874)

    def power_check(self):
        """体力检测"""
        screen = self._screen_shot.screenshot(self.r_o(0.4323, 0.2963, 0.13542, 0.05556))
        _, _, match = image_contrast('image/text_no_tili.png', screen)
        return match >= 0.9

    def use_fuel(self):
        """使用体力药"""
        pass

    def battle_monitor(self):
        """战斗情况检测"""
        time.sleep(1)
        screen = self._screen_shot.screenshot(self.r_o(0.2417, 0.2157, 0.521, 0.417))
        _, _, match = image_contrast('image/text_challengeSuccess.png', screen)

        return match >= 0.9

    def battle_again(self):
        """再次挑战"""
        self.click(0, 0, 0.640625, 0.875)
        time.sleep(1)
