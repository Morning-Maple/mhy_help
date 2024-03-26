import json
import os
import time
from datetime import datetime, timedelta

import cv2
import numpy as np
import pyautogui as pg
import pygetwindow as gw

import Types

w_left, w_top, w_width, w_height = 0, 0, 0, 0
current_dir = os.path.dirname(os.path.abspath(__file__))
region = (0, 0, 0, 0)
# 获取游戏窗口
game_window = gw.getWindowsWithTitle('崩坏：星穹铁道')[0]

with open('default_config.json', 'r') as f:
    config_default = json.load(f)
with open('config.json', 'r') as f:
    config = json.load(f)


def pathReturn(path):
    """
    返回图片所在路径
    Args:
        path (str): 图片名
    Returns:
        str: 图片所在路径
    """
    return os.path.join(current_dir, 'image', path)


def check_window():
    """
    初始化部分变量数据
    """
    global w_left, w_top, w_width, w_height, region, game_window
    if not game_window.isActive:
        # 防止最小化，同时激活窗口
        game_window.restore()
        game_window.activate()
        # 获取窗口的位置信息
        w_left, w_top, w_width, w_height = game_window.left, game_window.top, game_window.width, game_window.height
        region = (w_left, w_top, w_width, w_height)


def auto_do_daily():
    global w_left, w_top, w_width, w_height, region, game_window

    check_window()
    time.sleep(0.5)  # 等待窗口激活
    default_way()
    time.sleep(2)

    for item in config["mode"]:
        mode = item["mode"]  # 目标副本
        detail = item["detail"]  # 副本细节
        rounds = item["round"]  # 次数

        def check_value():
            mode1 = mode.split('.')[2]
            detail1 = detail.split('.')[2]
            try:
                _ = Types.ModeType[mode1]
            except KeyError:
                return False
            if rounds <= 0:
                return False
            match mode1:
                case 'NZHEJ':
                    try:
                        _ = Types.NZHEJMode[detail1]
                    except KeyError:
                        return False
                case 'NZHEC':
                    try:
                        _ = Types.NZHECMode[detail1]
                    except KeyError:
                        return False
                case 'NZXY':
                    try:
                        _ = Types.NZXYMode[detail1]
                    except KeyError:
                        return False
                case 'QSSD':
                    try:
                        _ = Types.QSSDMode[detail1]
                    except KeyError:
                        return False
                case 'LZYX':
                    try:
                        _ = Types.LZYXMode[detail1]
                    except KeyError:
                        return False
                case _:
                    return False
            return True

        res = check_value()
        if not res:
            print('数值有误')
            return False
        mode = getattr(getattr(Types, mode.split('.')[1]), mode.split('.')[2])
        detail = getattr(getattr(Types, detail.split('.')[1]), detail.split('.')[2])

        res = choose_mode(mode)
        if not res:
            print('模式选择失败')
            return False

        # 首次挑战
        time.sleep(3)
        next_rounds = 0
        current_rounds = 0
        if mode == Types.ModeType.NZHEJ and rounds > 6:
            next_rounds = rounds - 6
            current_rounds = 6
            res = choose_mode_detail(detail, mode, current_rounds)
        else:
            res = choose_mode_detail(detail, mode, rounds)
        if not res:
            print('挑战开始失败')
            return False
        res = watch_battle()
        if not res:
            print('战斗监测失败')
            return False

        # 重复挑战
        if mode == Types.ModeType.NZHEJ:
            rou = rounds / 6
            if rounds % 6 != 0:
                rou += 1
            for _ in range(rou):
                if next_rounds > 6:
                    res = battle_again(mode, current_rounds, 6)
                    if not res:
                        print('拟造花萼重复挑战失败')
                        return False
                    next_rounds -= 6
                else:
                    res = battle_again(mode, current_rounds, next_rounds)
                    if not res:
                        print('拟造花萼重复挑战失败')
                        return False
                res = watch_battle()
                if not res:
                    print(f'拟造花萼挑战失败')
                    return False

        for _ in range(rounds - 1):
            res = battle_again(mode)
            if not res:
                print(f'副本{mode}重复挑战失败')
                return False
            res = watch_battle()
            if not res:
                print(f'副本{mode}挑战失败')
                return False
        return True
    print('全部项目已完成！')


def screenshot(gray=True, regions=None, is_show=False):
    """
    对当前页面进行截图
    Args:
        gray (bool): 是否进行灰度处理
        regions:  截图区域，如None则使用全局配置
        is_show (bool): 是否临时展示
    Returns:
        Image: 截图的图片
    """
    global region
    if not regions:
        screen = pg.screenshot(region=region)
    else:
        screen = pg.screenshot(region=regions)

    if is_show:
        screen.show()

    if gray:
        screen = np.array(screen)
        screen = cv2.cvtColor(screen, cv2.COLOR_RGB2BGR)
        screen = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
    return screen


def watch_battle(t=6):
    """
    战斗监测
    Args:
        t: 副本挑战限制时间（分钟）
    Returns:
        bool: True为挑战成功，否则返回False
    """

    def isOpenDoubleSpeed(check_round=0):
        """
        开启二倍速
        Args:
            check_round (int): 当前检查轮数
        Returns：
            bool： True为开启成功，否则返回False
        """
        image_nods = cv2.imread(pathReturn('button_noDoubleSpeed.png'), cv2.IMREAD_GRAYSCALE)
        bo, loc = image_contrast(image_nods, screenshot(), expand=True, threshold=0.8)

        image_odab = cv2.imread(pathReturn('button_openDoubleSpeed.png'), cv2.IMREAD_GRAYSCALE)
        bo1, _ = image_contrast(image_odab, screenshot(), expand=True, threshold=0.8)
        if bo:
            x, y = loc
            pg.click(w_left + x, w_top + y)
            return isOpenDoubleSpeed(0)
        elif bo1:
            print('已处于二倍速')
            return True
        elif check_round >= 8:
            return False
        else:
            time.sleep(1)
            return isOpenDoubleSpeed(check_round + 1)

    time.sleep(5)
    isOpenDoubleSpeed(0)

    def openAutoBattle(check_round=0):
        """
        开启自动战斗
        Args:
            check_round (int): 当前检查轮数
        Returns：
            bool： True为开启成功，否则返回False
        """
        image_noab = cv2.imread(pathReturn('button_noAutoBattle.png'), cv2.IMREAD_GRAYSCALE)
        bo, btn_loc = image_contrast(image_noab, screenshot(), expand=True, threshold=0.8)

        image_ooab = cv2.imread(pathReturn('button_openAutoBattle.png'), cv2.IMREAD_GRAYSCALE)
        bo1, _ = image_contrast(image_ooab, screenshot(), expand=True, threshold=0.8)
        if bo:
            x, y = btn_loc
            pg.click(w_left + x, w_top + y)
            return openAutoBattle(0)
        elif bo1:
            print('已处于自动战斗')
            return True
        elif check_round >= 8:
            print('不处于自动状态且无法开启自动战斗')
            return False
        else:
            time.sleep(1)
            return openAutoBattle(check_round + 1)

    time.sleep(1)
    canFinish = openAutoBattle(0)
    if not canFinish:
        return False

    changeTime = datetime.now()

    def isFinsh(times=t):
        """
        检查是否已经完成挑战
        Args:
            times: 副本挑战限制时间（分钟）
        Returns:
            bool: True为已完成，否则返回False
        """
        image_finish = cv2.imread(pathReturn('text_challengeSuccess.png'), cv2.IMREAD_GRAYSCALE)
        bo, _ = image_contrast(image_finish, screenshot())
        if bo:
            return True
        elif datetime.now() - changeTime > timedelta(minutes=times):
            print('6分钟内未能检测到挑战成功，异常退出')
            return False
        else:
            time.sleep(10)
            return isFinsh()

    return isFinsh()


def battle_again(mode_type: Types.ModeType, current_rounds=1, next_rounds=1):
    time.sleep(3)
    if mode_type == Types.NZHEJMode and current_rounds != next_rounds:
        def leave(check_round=0):
            image1 = cv2.imread(pathReturn('button_leaveChallenge.png'), cv2.IMREAD_GRAYSCALE)
            b1, loc1 = image_contrast(image1, screenshot())
            if b:
                x1, y1 = loc1
                pg.click(w_left + x1, w_top + y1)
                return True
            elif check_round >= 4:
                return False
            else:
                return leave(check_round + 1)

        res = leave(0)
        if res:
            time.sleep(5)
            pg.press('f')
            time.sleep(3)
            ress = challengeRounds(next_rounds)
            if not ress:
                print(f'设置{next_rounds}轮次失败！')
                return False
            time.sleep(2)

            return challenge(mode_type, next_rounds)
        else:
            return False
    else:
        image = cv2.imread(pathReturn('button_again.png'), cv2.IMREAD_GRAYSCALE)
        b, loc = image_contrast(image, screenshot())
        if b:
            x, y = loc
            pg.click(w_left + x, w_top + y)

            res = noAllowAgain(0)
            if res:
                print('体力不足')
                return False
            return True
        else:
            print('再次挑战失败！')
            return False


def get_sx_email_q():
    """
    领取实训/邮件/钱
    Returns:
        tool: True成功，否则返回False
    """
    pg.press('esc')
    time.sleep(3)

    def get_sx():
        image = cv2.imread(pathReturn('button_zhinan.png'), cv2.IMREAD_GRAYSCALE)
        b, loc = image_contrast(image, screenshot(), True)
        if b:
            x, y = loc
            pg.click(w_left + x, w_top + y)
        else:
            print('找不到指南的点击图标！')
            return False

        while True:
            time.sleep(3)
            image_get = cv2.imread(pathReturn('button_get.png'), cv2.IMREAD_GRAYSCALE)
            b, loc = image_contrast(image_get, screenshot())
            if b:
                x, y = loc
                pg.click(w_left + x, w_top + y)
                time.sleep(0.5)
                pg.move(0, -100)
            else:
                break

        time.sleep(3)
        image_sx = cv2.imread(pathReturn('button_shixun.png'), cv2.IMREAD_GRAYSCALE)
        b, loc = image_contrast(image_sx, screenshot())
        if b:
            x, y = loc
            pg.click(w_left + x, w_top + y)
        else:
            print('找不到实训的点击图标！')
            return False

    # res = get_sx()
    # print(f'实训领取结果为：{res}')
    # pg.press('esc')
    # time.sleep(3)

    def get_email():
        image = cv2.imread(pathReturn('button_email1.png'), cv2.IMREAD_GRAYSCALE)
        b, loc = image_contrast(image, screenshot(), True)
        if b:
            x, y = loc
            pg.click(w_left + x, w_top + y)
        else:
            image = cv2.imread(pathReturn('button_email2.png'), cv2.IMREAD_GRAYSCALE)
            b, _ = image_contrast(image, screenshot(), True)
            if b:
                print('无邮件可领取！')
                return True
            else:
                print('找不到邮件的点击图标！')
                return False

        time.sleep(3)
        image = cv2.imread(pathReturn('button_all_get.png'), cv2.IMREAD_GRAYSCALE)
        b, loc = image_contrast(image, screenshot())
        if b:
            x, y = loc
            pg.click(w_left + x, w_top + y)
            time.sleep(1)
            pg.press('esc')
            time.sleep(1)
            pg.press('esc')
        else:
            print('邮件领取失败！')
            return False

    res = get_email()
    print(f'邮件领取结果为：{res}')
    time.sleep(3)

    def get_q():
        image = cv2.imread(pathReturn('button_q1.png'), cv2.IMREAD_GRAYSCALE)
        b, loc = image_contrast(image, screenshot(), True)
        if b:
            x, y = loc
            pg.click(w_left + x, w_top + y)
        else:
            image = cv2.imread(pathReturn('button_q2.png'), cv2.IMREAD_GRAYSCALE)
            b, _ = image_contrast(image, screenshot(), True)
            if b:
                print('没有钱可被领取！')
                return True
            else:
                print('找不到省略号的点击图标！')
                return False

        time.sleep(3)
        image = cv2.imread(pathReturn('button_myqz.png'), cv2.IMREAD_GRAYSCALE)
        b, loc = image_contrast(image, screenshot())
        if b:
            x, y = loc
            pg.click(w_left + x, w_top + y)
        else:
            print('找不到漫游签证的点击图标！')
            return False

        time.sleep(3)
        image = cv2.imread(pathReturn('button_get_q.png'), cv2.IMREAD_GRAYSCALE)
        b, loc = image_contrast(image, screenshot())
        if b:
            x, y = loc
            pg.click(w_left + x, w_top + y)
            time.sleep(1)
            pg.press('esc')
            time.sleep(1)
            pg.press('esc')
        else:
            print('找不到领取钱的点击图标！')
            return False

    res = get_q()
    print(f'助战奖励领取结果为：{res}')
    time.sleep(3)
    return True


def tspq():
    """
    探索派遣
    Returns:
        tool: True成功，否则返回False
    """
    pass


def default_way():
    """
    立即回到生存索引页面
    Returns:
        bool: True如果执行成功，否则返回False
    """
    pg.press('esc')
    time.sleep(1)
    pg.press('f1')
    time.sleep(1.75)
    image = cv2.imread(pathReturn('button_shengcunsuoyin.png'), cv2.IMREAD_GRAYSCALE)
    b, loc = image_contrast(image, screenshot(), True)
    if b:
        x, y = loc
        pg.click(w_left + x, w_top + y)
        return True
    else:
        print('找不到生存索引的点击图标！')
        return False


def image_contrast(
        image,
        screen,
        expand=False,
        threshold=0.9,
        method=cv2.TM_CCOEFF_NORMED,
        is_show_thr=False,
        is_show_res=False
):
    """
    点击目标图片
    Args:
        image (UMat): 模板图片
        screen (UMat): 截图
        expand (bool): 是否对图片进行边缘检测（若图片与模板只存在颜色不同，建议设为True）
        threshold (float): 阈值[0,1]（越高越精准）
        method (int): 处理方式
        is_show_thr (bool): 是否输出对比度
        is_show_res (bool): 是否输出匹配结果
    Returns:
        bool: True如果点击成功，否则返回False
        tuple: 匹配到的模板的中心位置
    """
    if expand:
        screen = cv2.Canny(screen, threshold1=100, threshold2=200)
        image = cv2.Canny(image, threshold1=100, threshold2=200)

    res = cv2.matchTemplate(screen, image, method)
    _, max_val, _, max_loc = cv2.minMaxLoc(res)
    if is_show_thr:
        print(max_val)
    if max_val >= threshold:
        h, w = image.shape[:2]
        center_loc = (max_loc[0] + w // 2, max_loc[1] + h // 2)
        return True, center_loc
    else:
        if is_show_res:
            print(time.strftime("%Y%m%d-%H%M%S", time.localtime()) + '：不匹配！')
        return False, None


def choose_mode(mode_type: Types.ModeType):
    """
    模式选择
    Args:
        mode_type: 模式枚举类
    Returns:
        bool: True成功选择，否则返回False
    """
    global w_left, w_top
    # 鼠标移动到左侧，开始检测
    pg.moveTo(w_left + config_default['leftSide']['x'], w_top + config_default['leftSide']['y'], duration=0.1)
    image = cv2.imread(pathReturn(mode_type.get_path), cv2.IMREAD_GRAYSCALE)
    check_window()

    def check_mode(check_round=0):
        """
        模式选择
        Returns:
            bool: True为成功，其余为失败
        """
        b, loc = image_contrast(image, screenshot())
        if b:
            return loc
        elif check_round >= 8:
            return None
        else:
            check_window()
            pg.moveTo(w_left + config_default['leftSide']['x'], w_top + config_default['leftSide']['y'], duration=0.5)
            for _ in range(4):
                pg.scroll(-600)
            time.sleep(1)
            return check_mode(check_round + 1)

    location = check_mode(0)
    if location:
        x, y = location
        pg.click(w_left + x, w_top + y)
        return True
    else:
        print('选择模式失败')
        return False


def choose_mode_detail(
        detail_type: Types.LZYXMode | Types.QSSDMode | Types.NZXYMode | Types.NZHECMode | Types.NZHEJMode,
        cs_str: Types.ModeType,
        rounds=1):
    """
    开始挑战
    Args:
        detail_type: 详细的模式
        cs_str: 模式
        rounds: 挑战次数，默认为1
    Returns:
        bool: True为开始挑战成功，否则返回False
    """
    global w_left, w_top
    pg.moveTo(w_left + config_default['rightSide']['x'], w_top + config_default['rightSide']['y'], duration=0.1)
    image = cv2.imread(pathReturn(detail_type.get_path), cv2.IMREAD_GRAYSCALE)
    check_window()

    # 副本传送实现（普通）
    def check_challenge_common(check_round=0):
        """
        副本选择（普通）
        Returns:
            bool: True为成功，其余为失败
        """
        b, loc = image_contrast(image, screenshot())
        if b:
            return loc
        elif check_round >= 8:
            return None
        else:
            check_window()
            pg.moveTo(w_left + config_default['rightSide']['x'], w_top + config_default['rightSide']['y'], duration=0.5)
            for _ in range(4):
                pg.scroll(-600)
            time.sleep(1)
            return check_challenge_common(check_round + 1)

    def check_challenge_special(check_round=0):
        """
        副本选择（特殊：拟造花萼金）
        Returns:
            bool: True为成功，其余为失败
        """
        image_loc = cv2.imread(pathReturn(detail_type.get_loc_path), cv2.IMREAD_GRAYSCALE)
        b1, loc1 = image_contrast(image_loc, screenshot(), True)
        if b1:
            x1, y1 = loc1
            pg.click(w_left + x1, w_top + y1)
            time.sleep(2)
            return check_challenge_common(0)
        elif check_round >= 8:
            return None
        else:
            check_window()
            pg.moveTo(w_left + config_default['rightSide']['x'], w_top + config_default['rightSide']['y'], duration=0.5)
            for _ in range(4):
                pg.scroll(-600)
            time.sleep(1)
            return check_challenge_special(check_round + 1)

    if detail_type == Types.NZHEJMode:
        location = check_challenge_special(0)
    else:
        location = check_challenge_common(0)

    if location:
        x, y = location
        pg.click(w_left + x + config_default[cs_str.name]['x'], w_top + y + config_default[cs_str.name]['y'])
        time.sleep(5)
    else:
        print('无法传送')
        return False

    ################

    return challenge(cs_str, rounds)


def challengeRounds(rounds: int = 1):
    """
    处理挑战次数（地脉/天赋材料）
    Args:
        rounds (int): 挑战次数
    Returns:
        bools: True为设置成功，否则为False
    """
    if not rounds >= 1 and rounds <= 6:
        print(f'{rounds}是不合法的数字')
        return False

    def getCurrentRounds(check_round=0):
        current_round_image = screenshot()
        for index, path in enumerate(Types.number_image_path):
            compare_image = cv2.imread(path)
            gray = cv2.cvtColor(compare_image, cv2.COLOR_BGR2GRAY)

            b, _ = image_contrast(gray, current_round_image, threshold=0.999)
            if b:
                return index + 1
        if check_round >= 2:
            return None
        else:
            return getCurrentRounds(check_round + 1)

    ids = getCurrentRounds(0)

    def handleAddOrReduce(path):
        image = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        b1, loc = image_contrast(image, screenshot())
        if b1:
            return loc
        else:
            return None

    if ids > rounds:
        location = handleAddOrReduce(pathReturn('button_black_reduce.png'))
        if not location:
            location = handleAddOrReduce(pathReturn('button_light_reduce.png'))

        if location:
            x, y = location
            for _ in range(ids - rounds):
                time.sleep(0.2)
                pg.click(w_left + x, w_top + y)
        else:
            print(f'目标要：{rounds}，但是检测为：{ids}，且无法减少！')
            return False
    elif ids < rounds:
        location = handleAddOrReduce(pathReturn('button_light_add.png'))
        if not location:
            location = handleAddOrReduce(pathReturn('button_black_add.png'))

        if location:
            x, y = location
            for _ in range(rounds - ids):
                time.sleep(0.2)
                pg.click(w_left + x, w_top + y)
        else:
            print(f'目标要：{rounds}，但是检测为：{ids}，且无法减少！')
            return False
    return True


# 进入副本选择（选择挑战次数在这儿进行）
def challenge(cs_str: Types.ModeType, rounds=1):
    def comeIn(check_round=0):
        """
        进入副本（地脉次数选择）
        Args:
            check_round: 检测次数
        Returns:
            bool: True如果成功，否则返回False
        """
        image_tz = cv2.imread(pathReturn('button_tiaozhan.png'), cv2.IMREAD_GRAYSCALE)
        bo1, btn_loc1 = image_contrast(image_tz, screenshot())
        if bo1:
            if cs_str == Types.ModeType.NZHEC or cs_str == Types.ModeType.NZHEJ:
                res = challengeRounds(rounds)
                if not res:
                    print(f'没有成功设置{rounds}次挑战次数')

            return btn_loc1
        elif check_round >= 8:
            return None
        else:
            time.sleep(1)
            return comeIn(check_round + 1)

    location = comeIn(0)
    if location:
        x, y = location
        pg.click(w_left + x, w_top + y)
    else:
        print('无法挑战-进入')
        return False

    res = noAllowAgain(0)
    if res:
        print('体力不足')
        return False

    # 进入队伍选择并且开始挑战
    def startChange(check_round=0):
        """
        选完队伍开始挑战
        Args:
            check_round: 检测次数
        Returns:
            bool: True如果成功，否则返回False
        """
        image_ks = cv2.imread(pathReturn('button_startTiaozhan.png'), cv2.IMREAD_GRAYSCALE)
        bo1, btn_loc1 = image_contrast(image_ks, screenshot())
        if bo1:
            return btn_loc1
        elif check_round >= 8:
            return None
        else:
            time.sleep(1)
            return comeIn(check_round + 1)

    time.sleep(3)
    location = startChange(0)

    if location:
        x, y = location
        pg.click(w_left + x, w_top + y)
        return True
    else:
        print('无法挑战-开始')
        return False


def noAllowAgain(check_round=0):
    """
    检查是否体力不足
    Args:
        check_round (int): 检查次数
    Returns:
        bool: True为体力不足，否则为False
    """
    image = cv2.imread(pathReturn('text_no_tili.png'), cv2.IMREAD_GRAYSCALE)
    bo, _ = image_contrast(image, screenshot())
    if bo:
        return True
    elif check_round >= 1:
        return False
    else:
        return noAllowAgain(check_round + 1)
