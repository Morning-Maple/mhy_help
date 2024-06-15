import json
import sys
import time
from enum import Enum

import pygetwindow as gw
import pyautogui as pg
from config.loguru_config import setup_logger
from newTypes import Types
from utils.ScreenShot import ScreenShot
from utils.ImagePositioning import ImagePositioning
import GameModeTypes as GMT
import utils.ConfigValueCheck as Check


class MouseMode(Enum):
    """鼠标移动枚举
    限制输入，用于鼠标定位游戏窗体的左侧滚动栏或右侧滚动栏
    """
    LEFT = 0
    RIGHT = 1


class ScrollDirection(Enum):
    """鼠标滚动枚举
    限制输入，用于确定对鼠标的滚动限制（只能上或下）
    """
    UP = 0
    DOWN = 1


class DailyScript:
    _instance = None
    _auto_battle = False
    _double_speed = False
    _screen_shot: ScreenShot = None
    _ip = None
    _pre = False
    _init_success = True

    user_config = None
    logs = None

    w_left = 0
    w_top = 0
    w_width = 0
    w_height = 0
    region = (0, 0, 0, 0)

    def __init__(self, mode: bool = False):
        """
        Args:
            mode(bool): True为开发模式，以DEBUG形式输出，False则是线上版本环境
        """
        try:
            self.config_set()
            self.logs_set(mode)
            self._screen_shot = ScreenShot(self.region)
            self.game_window_set()
            self._ip = ImagePositioning(mode)
            Check.check_config("config")
            self._pre = mode  # True就是开发模式，处于DEBUG状态
            self.logs.info("初始化完毕，正在执行！")
        except Exception as e:
            if self._pre:
                # 开发测试模式下异常需要直接抛出以定位问题位置
                raise e
            self.logs.warning(e)
            self._init_success = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = object.__new__(cls)
        return cls._instance

    def config_set(self):
        """配置文件初始化
        读取配置文件并且保存在全局
        """
        with open('config/config.json', 'r', encoding='utf-8') as f:
            self.user_config = json.load(f)

    def logs_set(self, mode: bool):
        """日志设定"""
        self.logs = setup_logger(mode)

    def click(self, loc):
        """鼠标点击事件
        接受一个坐标元组，然后执行点击此坐标在目标窗体内的位置，目标窗体位置由类自身属性维护
        Args:
            loc(tuple): 一个坐标元组，第一个元素是x，第二个元素是y
        Examples:
            >>> import pyautogui
            >>> windows_x = 50
            >>> windows_y = 100
            >>> locs = (10, 20)
            >>> self.click(locs)
            >>> # 相当于执行了下面
            >>> pyautogui.click(windows_x + 10, windows_y + 20)
        """
        x, y = loc
        pg.click(round(self.w_left + x), round(self.w_top + y))
        pg.move(-20, 0)

    def game_window_set(self):
        """配置窗口位置
        首次会初始化窗口位置的值，如果再次调用则会检测窗口是否有移动，有则会更新窗口位置数据
        """
        game_window = gw.getWindowsWithTitle('崩坏：星穹铁道')

        if game_window is None or len(game_window) <= 0:
            raise RuntimeError('找不到游戏窗口！')

        game_window = game_window[0]
        if not game_window.isActive:
            # 防止最小化，同时激活窗口
            game_window.restore()
            game_window.activate()

        if self.w_top != game_window.top:
            # 获取窗口的位置信息
            self.w_left, self.w_top, self.w_width, self.w_height = game_window.left, game_window.top, game_window.width, game_window.height
            self.region = (self.w_left, self.w_top, self.w_width, self.w_height)
            self._screen_shot.screen_regions = self.region

    def screenshot(self, region: tuple = None):
        """截图
        截图前会再次确认游戏窗体位置，然后再调用截图类进行截图
        Args:
            region(tuple): 截图区域，不填则采用游戏窗口区域
        Returns:
            ScreenShot类截取到的图片
        """
        self.game_window_set()
        return self._screen_shot.screenshot(region)

    def run_script(self):
        """脚本运行"""
        if self._init_success is False:
            return
        time.sleep(0.5)
        pg.press('M')
        time.sleep(1.5)

        try:
            if self.user_config["project"]["weiTuo"] == 1:
                self.logs.info(">>开始执行功能：委托派遣")
                self.wei_tuo()
                self.logs.info(">>>执行结束：委托派遣")

            if self.user_config["project"]["email"] == 1:
                self.logs.info(">>开始执行功能：邮件领取")
                self.email()
                self.logs.info(">>>执行结束：邮件领取")

            if self.user_config["project"]["zhuZhan"] == 1:
                self.logs.info(">>开始执行功能：助战奖励领取")
                self.help_money()
                self.logs.info(">>>执行结束：助战奖励领取")

            if self.user_config["project"]["fuBen"] == 1:
                self.logs.info(">>开始执行功能：副本挑战")
                self.fu_ben()
                self.logs.info(">>>执行结束：副本挑战")

            if self.user_config["project"]["shiXun"] == 1:
                self.logs.info(">>开始执行功能：实训点领取")
                self.shi_xun()
                self.logs.info(">>>执行结束：实训点领取")

            if self.user_config["project"]["xunLi"] == 1:
                self.logs.info(">>开始执行功能：无名勋礼领取")
                self.xun_li()
                self.logs.info(">>>执行结束：无名勋礼领取")
        except Exception as e:
            if self._pre:
                # 开发测试模式下异常需要直接抛出以定位问题位置
                raise e
            self.logs.warning(e)

    def wei_tuo(self):
        """委托派遣
        1. 打开手机，定位委托图标位置并点击
        2. 判断是否有派遣需要领取
        2-1. 没有委托领取则跳到步骤3
        2-2. 有委托则执行全部领取后，点击再次派遣
        3. 退回到游戏控制界面
        """
        time.sleep(2)
        pg.press('ESC')
        time.sleep(2)

        screen = self.screenshot()
        rel, loc = self._ip.target_prediction(screen, Types.button_weituo)
        self.click(loc)
        time.sleep(2)

        # 委托领取
        screen = self.screenshot()
        rel, loc = self._ip.target_prediction(screen, Types.button_receive_all)
        if rel == 0:
            self.logs.info('无委托需要被领取！')
        else:
            self.click(loc)
            time.sleep(1.5)

            # 再次派遣
            screen = self.screenshot()
            rel, loc = self._ip.target_prediction(screen, Types.button_weituo_again)
            self.click(loc)
            self.logs.info('委托领取成功并已经重新派遣！')
            time.sleep(2.5)
        pg.press('ESC')
        time.sleep(1)
        pg.press('ESC')

    def email(self):
        """邮件领取
        1. 打开手机，定位邮件图标位置并点击
        2. 判断是否有邮件需要领取，rel为0时则无邮件可领取，否则为有
        2-1. 没有邮件领取则跳到步骤3
        2-2. 有邮件则执行全部领取
        3. 退回到游戏控制界面
        """
        time.sleep(2)
        pg.press('ESC')
        time.sleep(1.5)

        screen = self.screenshot()
        _, loc = self._ip.target_prediction(screen, Types.button_email)
        self.click(loc)
        time.sleep(1.5)

        # 邮件领取
        screen = self.screenshot()
        rel, loc = self._ip.target_prediction(screen, Types.button_get_all, can_zero=True)
        if rel != 0:
            self.click(loc)
            self.logs.info("邮件领取成功!")
            time.sleep(1.5)
            pg.press('ESC')
        else:
            self.logs.info("无邮件可领取!")
        time.sleep(1.5)

        pg.press('ESC')
        time.sleep(1.5)
        pg.press('ESC')

    def help_money(self):
        """助战奖励
        1. 打开手机，定位委托图标位置并点击
        2. 判断是否有派遣需要领取，rel为0时则无邮件可领取，否则为有
        2-1. 没有委托领取则直接退回到游戏控制界面
        2-2. 有委托则执行全部领取后，再次派遣，然后退回到游戏控制界面
        """
        time.sleep(2)
        pg.press('ESC')
        time.sleep(1.5)

        screen = self.screenshot()
        _, loc = self._ip.target_prediction(screen, Types.button_more)
        self.click(loc)
        time.sleep(1)

        screen = self.screenshot()
        _, loc = self._ip.target_prediction(screen, Types.button_manyouqianzheng)
        self.click(loc)

        # 助战奖励领取
        screen = self.screenshot()
        rel, loc = self._ip.target_prediction(screen, Types.button_manyouqianzheng_get, can_zero=True)
        if rel != 0:
            self.click(loc)
            self.logs.info('助战奖励领取成功啾！')
            time.sleep(1.5)
            pg.press('ESC')
            time.sleep(1)
        else:
            self.logs.info('没有助战奖励可被领取！')

        time.sleep(1)
        pg.press('ESC')
        time.sleep(2)
        pg.press('ESC')

    def fu_ben(self):
        """
        副本挑战
        """
        plan = self.user_config["mode"]
        for item in plan:
            mode = item["mode"]
            detail = item["detail"]
            rounds = item["round"]

            mode = getattr(getattr(GMT, mode.split('.')[1]), mode.split('.')[2])
            detail = getattr(getattr(GMT, detail.split('.')[1]), detail.split('.')[2])

            self.choose_mode(mode, detail)
            self.choose_mode_detail(detail)
            self.enter_mode()
            self.battle_count(rounds)

        self.logs.info('副本挑战已完成！')

    def shi_xun(self):
        """实训领取
        1. 打开手机，定位指南图标位置并点击
        2. 点击每日实训图标
        3. 判断实训是否已经满，是则跳到步骤7
        4. 判断是否有领取图标
        4-1. 有领取图图标，则循环检测并且点击，直到检测失败
        4-2. 无领取图标，跳到步骤5
        5. 领取累积实训点奖励
        6. 判断本日活跃度是否已满，并且输出日志
        7. 退回到游戏控制界面
        """
        time.sleep(2)
        pg.press('ESC')
        time.sleep(1.5)

        screen = self.screenshot()
        _, loc = self._ip.target_prediction(screen, Types.button_zhinan)
        self.click(loc)
        time.sleep(1.5)

        screen = self.screenshot()
        _, loc = self._ip.target_prediction(screen, Types.button_shixun)
        self.click(loc)
        time.sleep(1)

        # 首次判断是否实训满，是则日志输出，然后直接返回
        rel, _ = self._ip.target_prediction(screen, Types.text_enough, can_zero=True, is_one=False)
        if rel != 0:
            self.logs('实训已满，无需领取')
            pg.press('ESC')
            time.sleep(1.5)
            pg.press('ESC')
            return

        # 循环检测领取按钮，直到拿全
        while True:
            time.sleep(0.5)
            screen = self.screenshot()
            rel, loc = self._ip.target_prediction(screen, Types.button_get, can_zero=True, is_one=False)
            if rel != 0:
                self.click(loc)
            else:
                break

        # 实训奖励领取
        time.sleep(1)
        rel, loc = self._ip.target_prediction(screen, Types.button_shixun_get, can_zero=True, is_one=False)
        if rel != 0:
            self.click(loc)
            time.sleep(1)
            pg.press('ESC')

        # 判断实训是否已满，日志输出
        time.sleep(1)
        rel, _ = self._ip.target_prediction(screen, Types.text_enough, can_zero=True, is_one=False)
        if rel == 0:
            self.logs.info('实训领取成功，但仍”>未满<“500实训点！')
        else:
            self.logs.info('实训领取成功，并且已经满了500实训点！')
            time.sleep(1)

        pg.press('ESC')
        time.sleep(1.5)
        pg.press('ESC')

    def xun_li(self):
        """勋礼领取
        1. 打开手机，定位无名勋礼图标位置并点击
        2. 点击任务图标
        3. 点击本周任务，判断是否有领取图标，有则执行点击领取，无则跳到步骤4
        4. 点击本期任务，判断是否有领取图标，有则执行点击领取，无则跳到步骤5
        5. 点击奖励图标，判断是否有领取图标，有则执行点击领取，无则跳到步骤6
        6. 退回到游戏控制界面
        """
        time.sleep(2)
        pg.press('ESC')
        time.sleep(1.5)

        screen = self.screenshot()
        _, loc = self._ip.target_prediction(screen, Types.button_xunli)
        self.click(loc)
        time.sleep(2)

        screen = self.screenshot()
        _, loc = self._ip.target_prediction(screen, Types.button_xunli_renwu)
        self.click(loc)
        time.sleep(1)

        # --任务部分
        # 本周任务
        screen = self.screenshot()
        _, loc = self._ip.target_prediction(screen, Types.button_xunli_renwu_week)
        self.click(loc)
        time.sleep(1)

        screen = self.screenshot()
        rel, loc = self._ip.target_prediction(screen, Types.button_receive_all, can_zero=True)
        if rel != 0:
            self.click(loc)
            self.logs.info('领取了本周任务的所有可领取的进度')
            time.sleep(3)

        # 本期任务
        screen = self.screenshot()
        _, loc = self._ip.target_prediction(screen, Types.button_xunli_renwu_version)
        self.click(loc)
        time.sleep(1)

        screen = self.screenshot()
        rel, loc = self._ip.target_prediction(screen, Types.button_receive_all, can_zero=True)
        if rel != 0:
            self.click(loc)
            self.logs.info('领取了>本期<任务的所有可领取的进度')
            time.sleep(3)

        # --奖励部分
        screen = self.screenshot()
        _, loc = self._ip.target_prediction(screen, Types.button_xunli_jiangli)
        self.click(loc)
        time.sleep(1)

        screen = self.screenshot()
        rel, loc = self._ip.target_prediction(screen, Types.button_receive_all, can_zero=True)
        if rel != 0:
            self.click(loc)
            self.logs.info('领取了无名勋礼中所有可领取的奖励')
            time.sleep(1.5)
            pg.press('ESC')
            time.sleep(1)

        self.logs.info('勋礼执行完成')
        pg.press('ESC')
        time.sleep(1.5)
        pg.press('ESC')

    def choose_mode(self, mode: GMT.ModeType, detail: GMT.NZHEJMode = None):
        """模式大类选择
        右侧导航栏模式选择
        Args:
            mode(GMT.ModeType): 模式大类枚举
            detail(GMT.NZHEJMode): 如果模式为拟造花萼金，那么此项必填
        """
        if mode == GMT.NZHEJMode and detail is None:
            raise ValueError('模式为拟造花萼(金)时，第二参数不能为空！')

        time.sleep(2)
        pg.press('ESC')
        time.sleep(1.5)

        screen = self.screenshot()
        _, loc = self._ip.target_prediction(screen, Types.button_zhinan)
        self.click(loc)
        time.sleep(1.5)

        screen = self.screenshot()
        _, loc = self._ip.target_prediction(screen, Types.button_suoying)
        self.click(loc)
        time.sleep(1.5)

        # 开始寻找大类
        find = 0
        while True:
            find += 1
            screen = self.screenshot()
            rel, loc = self._ip.target_prediction(screen, mode.get_types, can_zero=True, threshold=0.9)
            if rel == 0:
                self.mouse_handle(MouseMode.LEFT, scroll=True)
            else:
                self.click(loc)
                time.sleep(1)
                break

            # 如果检测到底部了还没找到，并且检测轮次，则只检测多一次，提高响应
            screen = self.screenshot()
            rel, _ = self._ip.target_prediction(screen, Types.LZYX, can_zero=True, threshold=0.9)
            if rel != 0 and find < 4:
                find = 4
                continue

            if find >= 4:
                raise ValueError(f'找不到模式:{mode.get_desc}！')

        if mode == GMT.NZHEJMode:
            self.choose_mode_NZHEJ_country(detail)

    def choose_mode_NZHEJ_country(self, mode: GMT.NZHEJMode):
        """拟造花萼（金）模式下，选择地区
        拟造花萼（金）模式下，选择地区（雅利洛6，仙舟，匹诺康尼）
        Args:
            mode(GMT.NZHEJMode): 拟造花萼（金）枚举类的枚举
        """
        screen = self.screenshot()
        _, loc = self._ip.target_prediction(screen, mode.get_country, can_zero=True, threshold=0.9)
        self.click(loc)
        time.sleep(1.5)

    def choose_mode_detail(self, mode: GMT.NZHEJMode | GMT.NZHECMode | GMT.NZXYMode | GMT.QSSDMode | GMT.LZYXMode):
        """模式小类选择
        左侧导航栏模式选择
        Args:
            mode(GMT.NZHEJMode | GMT.NZHECMode | GMT.NZXYMode | GMT.QSSDMode | GMT.LZYXMode): 模式小类枚举
        """

        def last_mode_set():
            """为每个模式的最底层目标进行赋值"""
            match mode.__class__:
                case GMT.NZHEJMode:
                    # 底部是信用点（钱）
                    return Types.NZHEJ_Q
                case GMT.NZHECMode:
                    # 底部是虚无丹鼎司的行迹材料
                    return GMT.NZHECMode.XW_DDS.get_types
                case GMT.NZXYMode:
                    # 底部是突破素材副本职司之形
                    return GMT.NZXYMode.ZS.get_types
                case GMT.QSSDMode:
                    # 底部是遗器副本死水钟表匠套
                    return GMT.QSSDMode.MQ.get_types
                case GMT.LZYXMode:
                    # 底部是周本尘梦的赞礼
                    return GMT.LZYXMode.CMDZL.get_types

        detail_types: Types = last_mode_set()

        find = 0
        while True:
            find += 1
            screen = self.screenshot()
            loc = self._ip.target_prediction_one_to_many(
                screen, mode.get_types, Types.button_teleport, Types.button_follow, threshold=0.9, can_zero_a=True)
            if loc[0] == 0:
                self.mouse_handle(MouseMode.RIGHT, scroll=True)
            else:
                self.click(loc)
                time.sleep(1)
                break

            # 如果检测到底部了还没找到，并且检测轮次，则只检测多一次，提高响应
            screen = self.screenshot()
            rel, _ = self._ip.target_prediction(screen, detail_types, threshold=0.9, can_zero=True)
            if rel != 0 and find < 16:
                find = 16
                continue

            if find >= 16:
                raise ValueError(f'找不到模式:{mode.get_desc}！')

        time.sleep(4)

    def enter_mode(self):
        """进入挑战"""
        time.sleep(2)
        screen = self.screenshot()
        _, loc = self._ip.target_prediction(screen, Types.button_challenge)
        self.click(loc)
        time.sleep(2)

        screen = self.screenshot()
        _, loc = self._ip.target_prediction(screen, Types.button_start)
        self.click(loc)
        time.sleep(2)

    def power_check(self):
        """体力检测
        检测是否体力不足，是则返回True，否则返回False
        Returns:
            bool: True，如果体力不足，否则返回False
        """
        time.sleep(2)
        screen = self.screenshot()
        rel, _ = self._ip.target_prediction(screen, Types.text_no_power, can_zero=True, threshold=0.8)
        time.sleep(1)
        if rel != 0:
            screen = self.screenshot()
            _, loc = self._ip.target_prediction(screen, Types.button_cancel)
            self.click(loc)
            time.sleep(1)
            return True
        else:
            return False

    def use_fuel(self):
        """使用体力药"""
        pass

    def battle_count(self, count):
        """副本战斗处理
        处理每个副本的循环挑战逻辑和执行情况，如果参数为0，没有体力后会自动退出执行下一步，否则会抛出体力不足的异常
        Args:
            count(int): 需要挑战的次数
        Raise:
            RuntimeError: 没打过副本，挑战失败，超时
        """
        progress = (count - 1, count)
        rounds = progress[0]
        logs_output = True

        # count为0则是一直挑战到体力不足为止
        if count == 0:
            logs_output = False
            rounds = 99999

        for _ in range(rounds):
            # 战斗监测（成功、失败、超时）
            res = self.battle_monitor()
            if res is False:
                raise RuntimeError('副本挑战失败！')

            # 再次战斗
            self.battle_again()
            # 体力监测
            res = self.power_check()
            if res is True:
                if logs_output:
                    self.logs.info(f'进行到({progress[0]}/{progress[1]})时，开拓力不足以进行下一轮战斗')
                else:
                    break

        # 退出副本，准备处理下一个挑战
        time.sleep(1)
        screen = self.screenshot()
        _, loc = self._ip.target_prediction(screen, Types.button_leave, can_zero=True)
        self.click(loc)
        time.sleep(8)

    def battle_monitor(self):
        """战斗情况监测
        每两秒检测一次战斗情况，如果300秒(五分钟)内挑战成功，返回True，否则返回False
        Returns:
            bool: 300秒(五分钟)内挑战成功，返回True，否则返回False
        """
        start_time = time.time()
        while round(time.time() - start_time) < 300:
            screen = self.screenshot()
            # 挑战成功
            rel, _ = self._ip.target_prediction(screen, Types.text_success, can_zero=True)
            if rel != 0:
                time.sleep(2)
                return True

            # 挑战失败
            rel, _ = self._ip.target_prediction(screen, Types.text_fail, can_zero=True)
            if rel != 0:
                self.logs.info('怎么回事？你没打过啾！')
                return False
            time.sleep(2)
        self.logs.info(f'用时超过了{300}秒，挑战超时啾！')
        return False

    def battle_again(self):
        """再次挑战"""
        time.sleep(3)
        for _ in range(8):
            time.sleep(0.5)
            screen = self.screenshot()
            rel, loc = self._ip.target_prediction(screen, Types.button_again)
            if rel != 0:
                self.click(loc)
                break

    def mouse_handle(self, mode: MouseMode, direction: ScrollDirection = ScrollDirection.DOWN, scroll=False, count=8):
        """鼠标事件处理
        支持鼠标移动到窗体的左侧或右侧导航栏，并支持在这些导航栏处滚动它们
        Args:
            mode(MouseMode): 定义鼠标是移动到左侧导航栏还是右侧导航栏
            direction(ScrollDirection): 定义滚动方向，默认为向下
            scroll(bool): 是否开启鼠标滚动，默认为False
            count(int): 鼠标滚动次数，默认为8
        Examples:
            >>> # 移动到右侧导航栏，然后向上滚动六次
            >>> self.mouse_handle(MouseMode.RIGHT, ScrollDirection.UP, True, 6)
        """
        match mode:
            case mode.LEFT:
                pg.moveTo(self.w_left + 0.23 * self.w_width, self.w_top + 0.53 * self.w_height)
            case mode.RIGHT:
                pg.moveTo(self.w_left + 0.81 * self.w_width, self.w_top + 0.54 * self.w_height)
            case _:
                raise ValueError(f'{mode}的值不合法！')

        time.sleep(0.1)
        if scroll:
            standard = 100
            if direction is ScrollDirection.DOWN:
                standard = -standard
            for _ in range(count):
                pg.scroll(standard)
            time.sleep(1)


# if __name__ == "__main__":
#     # DailyScript(True).run_script()
#     DailyScript(True).run_script()
#     # DailyScript(True).mouse_handle(MouseMode.RIGHT, scroll=True, count=8)
#     sys.exit()
