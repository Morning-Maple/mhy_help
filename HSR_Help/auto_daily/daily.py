import json
import os
import time
from datetime import datetime, timedelta

import cv2
import pyautogui as pg
import pygetwindow as gw

import Types
from utils.utils import ImageOperation, repeat_check

w_left, w_top, w_width, w_height = 0, 0, 0, 0
current_dir = os.path.dirname(os.path.abspath(__file__))
region = (0, 0, 0, 0)
# 获取游戏窗口
game_window = gw.getWindowsWithTitle('崩坏：星穹铁道')[0]

with open('config/default_config.json', 'r', encoding='utf-8') as f1:
    config_default = json.load(f1)
with open('config/config.json', 'r', encoding='utf-8') as f2:
    config = json.load(f2)


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

    project = config["mode"]
    if project is None:
        project = []
    for item in project:
        mode = item["mode"]  # 目标副本
        detail = item["detail"]  # 副本细节
        rounds = item["round"]  # 次数

        def check_value():
            """数值检查"""
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
            print(config_default['text']['settingError'])
            return False
        mode = getattr(getattr(Types, mode.split('.')[1]), mode.split('.')[2])
        detail = getattr(getattr(Types, detail.split('.')[1]), detail.split('.')[2])

        res = choose_mode(mode)
        if not res:
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
            return False
        res = watch_battle()
        if not res:
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
                        return False
                    next_rounds -= 6
                else:
                    res = battle_again(mode, current_rounds, next_rounds)
                    if not res:
                        return False
                res = watch_battle()
                if not res:
                    return False

        for _ in range(rounds - 1):
            res = battle_again(mode)
            if not res:
                return False
            res = watch_battle()
            if not res:
                return False
        return True
    print('全部项目已完成！')


def watch_battle(t=6):
    """
    战斗监测
    Args:
        t: 副本挑战限制时间（分钟）
    Returns:
        bool: True为挑战成功，否则返回False
    """

    # 二倍速检测
    def check_double_speed():
        return repeat_check(
            image1=cv2.imread('image/button_noDoubleSpeed.png', cv2.IMREAD_GRAYSCALE),
            regions=region,
            expand=[ImageOperation.CANNY],
            image2=cv2.imread('image/button_openDoubleSpeed.png', cv2.IMREAD_GRAYSCALE),
            rounds=8,
            sleep=1,
            threshold=0.8
        )

    time.sleep(5)
    results, loc = check_double_speed()
    res = judgment_results(
        (results, loc),
        config_default['text']['doubleSpeedOpening'],
        config_default['text']['successOpenDoubleSpeed'],
        config_default['text']['canNotOpenDoubleSpeed'],
        expand=check_double_speed()
    )
    if not res:
        print(config_default['text']['error'])

    # 自动战斗检测
    def check_auto_battle():
        return repeat_check(
            image1=cv2.imread('image/button_noAutoBattle.png', cv2.IMREAD_GRAYSCALE),
            regions=region,
            expand=[ImageOperation.CANNY],
            image2=cv2.imread('image/button_openAutoBattle.png', cv2.IMREAD_GRAYSCALE),
            rounds=8,
            sleep=1,
            threshold=0.8
        )

    time.sleep(1)
    results, loc = check_auto_battle()
    res = judgment_results(
        (results, loc),
        config_default['text']['autoBattleOpening'],
        config_default['text']['successOpenAutoBattle'],
        config_default['text']['canNotOpenAutoBattle'],
        expand=check_double_speed()
    )
    if not res:
        print(config_default['text']['error'])
        return False

    # 监视战斗是否结束
    changeTime = datetime.now()

    def check_finish(times=t):
        """
        检测战斗是否结束
        Args:
            times (int): 挑战限制时间（分钟）
        Returns:
            bool: True为挑战成功，其余为挑战失败
        """
        is_finsh, _ = repeat_check(
            image2=cv2.imread('image/text_challengeSuccess.png.png', cv2.IMREAD_GRAYSCALE),
            regions=region,
            expand=[ImageOperation.CANNY],
            rounds=1,
            threshold=0.8
        )
        if is_finsh:
            return True
        elif datetime.now() - changeTime > timedelta(minutes=times):
            print(f'{config_default["text"]["timeOutInBattle"]}{times}分钟')
        else:
            time.sleep(10)
            return check_finish()

    return check_finish(t)


def battle_again(mode_type: Types.ModeType, current_rounds=1, next_rounds=1):
    """
    再次挑战
    Args:
        mode_type: 模式
        current_rounds: 当前挑战轮次（非拟造花萼金可不填）
        next_rounds: 下一次挑战轮次（非拟造花萼金可不填）
    """
    time.sleep(3)
    # 副本为拟造花萼金且下一次挑战次数与上一次挑战次数不同
    if mode_type == Types.NZHEJMode and current_rounds != next_rounds:
        results, loc = repeat_check(
            image1=cv2.imread('image/button_leaveChallenge.png', cv2.IMREAD_GRAYSCALE),
            regions=region,
            expand=[],
            rounds=4,
        )
        res = judgment_results(
            (results, loc),
            is_show_true_and_none=False,
            is_show_true_and_have=False,
            false=config_default['text']['canLeaveChallenge']
        )
        if res:
            time.sleep(5)
            pg.press('f')
            time.sleep(3)
            ress = challenge_rounds(next_rounds)
            if not ress:
                print(f'设置{next_rounds}轮次失败！')
                return False
            time.sleep(2)

            return challenge(mode_type, next_rounds)
        else:
            print(config_default['text']['error'])
            return False

    else:
        # 普通再次挑战直接点击再来一次就行
        results, loc = repeat_check(
            image1=cv2.imread('image/button_again.png', cv2.IMREAD_GRAYSCALE),
            regions=region,
            expand=[],
            rounds=4,
            sleep=1,
        )
        res = judgment_results(
            (results, loc),
            is_show_true_and_none=False,
            is_show_true_and_have=False,
            false=config_default['text']['canNoAgainChallenge']
        )
        if res:
            isAllow = no_allow_again(0)
            if isAllow:
                print(config_default['text']['noPower'])
                return False
            return True
        else:
            return False


def get_sx_email_q():
    """
    领取实训/邮件/钱
    Returns:
        tool: True成功，否则返回False
    """
    pg.press('esc')
    time.sleep(3)

    # 实训领取
    def get_sx():
        """
        领取实训奖励
        """
        results, loc = repeat_check(
            image1=cv2.imread('image/button_zhinan_have.png', cv2.IMREAD_GRAYSCALE),
            image2=cv2.imread('image/button_zhinan_none.png', cv2.IMREAD_GRAYSCALE),
            regions=region,
            expand=[ImageOperation.CANNY],
            rounds=4,
            sleep=1,
        )
        res1 = judgment_results(
            (results, loc),
            true_and_none=config_default['text']['noShiXunCanGet'],
            is_show_true_and_have=False,
            false=f"{config_default['text']['canNoFindButton']}{'指南'}",
        )
        if not res1:
            return False
        elif loc is None:
            return True

        rounds = 0
        while True:
            time.sleep(3)
            results, loc = repeat_check(
                image1=cv2.imread('image/button_get.png', cv2.IMREAD_GRAYSCALE),
                regions=region,
                expand=[],
                rounds=2,
                sleep=1,
            )
            res2 = judgment_results(
                (results, loc),
                is_show_true_and_none=False,
                is_show_true_and_have=False,
                is_show_false=False
            )
            if res2:
                time.sleep(0.5)
                pg.move(0, -100)
            elif rounds < 4:
                rounds += 1
                continue
            else:
                break

        time.sleep(3)
        results, loc = repeat_check(
            image1=cv2.imread('image/button_shixun.png', cv2.IMREAD_GRAYSCALE),
            regions=region,
            expand=[],
            rounds=4,
            sleep=1,
        )
        return judgment_results(
            (results, loc),
            is_show_true_and_none=False,
            true_and_have=config_default['text']['successGetShiXun'],
            false=f"{config_default['text']['canNoFindButton']}{'领取实训'}",
        )

    res_sx = get_sx()
    if not res_sx:
        return False
    else:
        time.sleep(1)
        pg.press('esc')
        time.sleep(3)
        pg.press('esc')

    time.sleep(3)

    def get_email():
        """
        邮件领取
        """
        results, loc = repeat_check(
            image1=cv2.imread('image/button_email_have.png', cv2.IMREAD_GRAYSCALE),
            image2=cv2.imread('image/button_email_none.png', cv2.IMREAD_GRAYSCALE),
            regions=region,
            expand=[ImageOperation.CANNY],
            rounds=4,
            sleep=1,
        )
        res1 = judgment_results(
            (results, loc),
            true_and_none=config_default['text']['noEmailCanGet'],
            is_show_true_and_have=False,
            false=f"{config_default['text']['canNoFindButton']}{'邮件'}",
        )
        if not res1:
            return False
        elif loc is None:
            return True

        time.sleep(3)
        results, loc = repeat_check(
            image1=cv2.imread('image/button_all_get.png', cv2.IMREAD_GRAYSCALE),
            regions=region,
            expand=[],
            rounds=4,
            sleep=1,
        )
        return judgment_results(
            (results, loc),
            is_show_true_and_none=False,
            is_show_true_and_have=config_default['text']['successGetEmail'],
            false=config_default['text']['emailGetFail'],
        )

    res_email = get_email()
    if not res_email:
        return False
    else:
        time.sleep(1)
        pg.press('esc')
        time.sleep(1)
        pg.press('esc')

    time.sleep(3)

    def get_q():
        """
        领取助战奖励
        """
        results, loc = repeat_check(
            image1=cv2.imread('image/button_q_have.png', cv2.IMREAD_GRAYSCALE),
            image2=cv2.imread('image/button_q_none.png', cv2.IMREAD_GRAYSCALE),
            regions=region,
            expand=[ImageOperation.CANNY],
            rounds=4,
            sleep=1,
        )
        res1 = judgment_results(
            (results, loc),
            true_and_none=config_default['text']['noMoneyGet'],
            is_show_true_and_have=False,
            false=f"{config_default['text']['canNoFindButton']}省略号",
        )
        if not res1:
            return False
        elif loc is None:
            return True

        time.sleep(3)
        results, loc = repeat_check(
            image1=cv2.imread('image/button_myqz.png', cv2.IMREAD_GRAYSCALE),
            regions=region,
            expand=[],
            rounds=4,
            sleep=1,
        )
        res1 = judgment_results(
            (results, loc),
            is_show_true_and_none=False,
            is_show_true_and_have=False,
            false=f"{config_default['text']['canNoFindButton']}漫游签证",
        )
        if not res1:
            return False

        time.sleep(3)
        results, loc = repeat_check(
            image1=cv2.imread('image/button_get_q.png', cv2.IMREAD_GRAYSCALE),
            regions=region,
            expand=[],
            rounds=4,
            sleep=1,
        )
        return judgment_results(
            (results, loc),
            is_show_true_and_none=False,
            is_show_true_and_have=config_default['text']['successGetMoney'],
            false=f"{config_default['text']['canNoFindButton']}领取助战奖励",
        )

    res_q = get_q()
    if not res_q:
        return False
    else:
        time.sleep(1)
        pg.press('esc')
        time.sleep(1)
        pg.press('esc')

    return True


def wt():
    """
    探索派遣/委托
    Returns:
        tool: True成功，否则返回False
    """
    pg.press('esc')
    time.sleep(3)

    results, loc = repeat_check(
        image1=cv2.imread('image/button_weituo_have.png', cv2.IMREAD_GRAYSCALE),
        regions=region,
        expand=[],
        image2=cv2.imread('image/button_weituo_no.png', cv2.IMREAD_GRAYSCALE),
        rounds=4,
        sleep=1,
        threshold=0.99,
        is_show_detail=True
    )
    res = judgment_results(
        (results, loc),
        true_and_none=config_default['text']['noWeiTuoCanHandle'],
        is_show_true_and_have=False,
        false=f"{config_default['text']['canNoFindButton']}委托",
    )
    if not res:
        return False
    elif loc is None:
        return True

    time.sleep(3)
    results, loc = repeat_check(
        image1=cv2.imread('image/button_one_click_get_1.png', cv2.IMREAD_GRAYSCALE),
        regions=region,
        expand=[],
        rounds=4,
        sleep=1,
    )
    res = judgment_results(
        (results, loc),
        is_show_true_and_none=False,
        is_show_true_and_have=False,
        false=f"{config_default['text']['canNoFindButton']}一键领取",
    )
    if not res:
        return False

    time.sleep(3)
    results, loc = repeat_check(
        image1=cv2.imread('image/button_again_weituo.png', cv2.IMREAD_GRAYSCALE),
        regions=region,
        expand=[],
        rounds=4,
        sleep=1,
    )
    res = judgment_results(
        (results, loc),
        is_show_true_and_none=False,
        true_and_have=config_default['text']['successGetWeiTuo'],
        false=f"{config_default['text']['canNoFindButton']}再次派遣",
    )
    if not res:
        return False

    time.sleep(2)
    pg.press('esc')
    time.sleep(2)
    pg.press('esc')
    return True


def xl():
    """
    无名勋礼
    """
    pg.press('esc')
    time.sleep(3)

    results, loc = repeat_check(
        image1=cv2.imread('image/button_xl_have.png', cv2.IMREAD_GRAYSCALE),
        regions=region,
        expand=[],
        image2=cv2.imread('image/button_xl_none.png', cv2.IMREAD_GRAYSCALE),
        rounds=4,
        sleep=1,
        threshold=0.99,
    )
    res = judgment_results(
        (results, loc),
        true_and_none=config_default['text']['noXunLiGet'],
        is_show_true_and_have=False,
        false=f"{config_default['text']['canNoFindButton']}无名勋礼",
    )
    if not res:
        return False
    elif loc is None:
        return True

    results, loc = repeat_check(
        image1=cv2.imread('image/button_xl_rw_have.png', cv2.IMREAD_GRAYSCALE),
        regions=region,
        expand=[],
        image2=cv2.imread('image/button_xl_rw_none.png', cv2.IMREAD_GRAYSCALE),
        rounds=4,
        sleep=1,
        threshold=0.99,
    )
    res = judgment_results(
        (results, loc),
        true_and_none=config_default['text']['noXunLiRenWuGet'],
        is_show_true_and_have=False,
        false=f"{config_default['text']['canNoFindButton']}无名勋礼——任务",
    )
    if not res:
        return False
    elif loc is not None:
        # 无名勋礼的任务需要领取，领取完毕跳回奖励页面
        results1, loc1 = repeat_check(
            image1=cv2.imread('image/button_one_click_get_1.png', cv2.IMREAD_GRAYSCALE),
            regions=region,
            expand=[],
            rounds=4,
            sleep=1,
        )
        # 不考虑结果，因为有可能本期任务存在红点而导致任务有红点，但是此时是没有“一键领取”标识的
        judgment_results(
            (results1, loc1),
            is_show_true_and_none=False,
            is_show_true_and_have=False,
            is_show_false=False,
        )
        time.sleep(3)

        results1, loc1 = repeat_check(
            image1=cv2.imread('image/button_xl_jl_have.png', cv2.IMREAD_GRAYSCALE),
            image2=cv2.imread('image/button_xl_jl_none.png', cv2.IMREAD_GRAYSCALE),
            regions=region,
            expand=[],
            rounds=4,
            threshold=0.99,
            sleep=1,
        )
        res1 = judgment_results(
            (results1, loc1),
            true_and_none=config_default['text']['noXunLiJiangLiGet'],
            is_show_true_and_have=False,
            false=f"{config_default['text']['canNoFindButton']}无名勋礼——奖励",
        )
        if not res1:
            return False
        elif loc1 is None:
            return True

    # 奖励判断领取逻辑
    results, loc = repeat_check(
        image1=cv2.imread('image/button_one_click_get_2.png', cv2.IMREAD_GRAYSCALE),
        regions=region,
        expand=[],
        rounds=4,
        sleep=1,
    )
    res = judgment_results(
        (results, loc),
        true_and_none=config_default['text']['noXunLiJiangLiGet'],
        true_and_have=config_default['text']['successGetXunLiJiangLi'],
        false=f"{config_default['text']['canNoFindButton']}无名勋礼——奖励——一键领取",
    )
    if not res:
        return False
    time.sleep(2)
    pg.press('esc')
    time.sleep(2)
    pg.press('esc')
    return True


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

    results, loc = repeat_check(
        regions=region,
        expand=[ImageOperation.CANNY],
        image2=cv2.imread('image/button_shengcunsuoyin.png', cv2.IMREAD_GRAYSCALE),
        rounds=3,
        sleep=1,
    )
    return judgment_results(
        (results, loc),
        is_show_true_and_none=False,
        is_show_true_and_have=False,
        false=f"{config_default['text']['canNoFindButton']}生存实训",
    )


def choose_mode(mode_type: Types.ModeType):
    """
    模式选择
    Args:
        mode_type: 模式枚举类
    Returns:
        bool: True成功选择，否则返回False
    """
    # 鼠标移动到左侧，开始检测
    pg.moveTo(w_left + config_default['leftSide']['x'], w_top + config_default['leftSide']['y'], duration=0.1)
    check_window()
    image = cv2.imread(mode_type.get_path, cv2.IMREAD_GRAYSCALE)

    def check_mode(check_round=0):
        """
        模式选择
        Returns:
            bool: True为成功，其余为失败
        """
        if check_round > 6:
            return None

        results, loc = repeat_check(
            regions=region,
            expand=[],
            image2=image,
            rounds=4,
            sleep=1,
        )

        res = judgment_results(
            (results, loc),
            is_show_true_and_none=False,
            is_show_true_and_have=False,
            is_show_false=False,
        )
        if res:
            return True
        else:
            check_window()
            pg.moveTo(w_left + config_default['leftSide']['x'], w_top + config_default['leftSide']['y'], duration=0.5)
            for _ in range(4):
                pg.scroll(-600)
            time.sleep(1)
            return check_mode(check_round + 1)

    res_check_mode = check_mode(0)
    if res_check_mode:
        return True
    else:
        print(config_default['text']['chooseModeFail'])
        return False


def choose_mode_detail(
        detail_type: Types.LZYXMode | Types.QSSDMode | Types.NZXYMode | Types.NZHECMode | Types.NZHEJMode,
        cs_str: Types.ModeType,
        rounds=1
):
    """
    开始挑战
    Args:
        detail_type: 详细的模式
        cs_str: 模式
        rounds: 挑战次数，默认为1
    Returns:
        bool: True为开始挑战成功，否则返回False
    """
    pg.moveTo(w_left + config_default['rightSide']['x'], w_top + config_default['rightSide']['y'], duration=0.1)

    check_window()

    # 副本传送实现（普通）
    def check_challenge_common(check_round=0):
        """
        副本选择（普通）
        Returns:
            bool: True为成功，其余为失败
        """
        if check_round > 8:
            return None

        results, loc = repeat_check(
            regions=region,
            expand=[],
            image1=cv2.imread(detail_type.get_path, cv2.IMREAD_GRAYSCALE),
            rounds=2,
            sleep=1,
        )
        if results:
            return loc
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
        if check_round > 8:
            return None

        results, loc = repeat_check(
            regions=region,
            expand=[ImageOperation.CANNY],
            image1=cv2.imread(detail_type.get_loc_path, cv2.IMREAD_GRAYSCALE),
            rounds=2,
            sleep=1,
        )

        res = judgment_results(
            (results, loc),
            is_show_true_and_none=False,
            is_show_true_and_have=False,
            false=config_default['text']['canChooseLocationChallenge']
        )
        if res:
            time.sleep(2)
            return check_challenge_common(0)
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
        print(config_default['text']['canNoTeleport'])
        return False

    ################

    return challenge(cs_str, rounds)


def challenge_rounds(rounds: int = 1):
    """
    处理挑战次数（地脉/天赋材料）
    Args:
        rounds (int): 挑战次数
    Returns:
        bools: True为设置成功，否则为False
    """
    if not rounds >= 1 and rounds <= 6:
        print(f"{config_default['text']['noAllowNumber']}{rounds}")
        return False

    def getCurrentRounds(check_round=2):
        """
        获取当前挑战轮数
        Args:
            check_round (int): 检查轮数
        Returns:
            int: 范围1到6的整数，若返回None，则说明检测失败
        """
        for index, path in enumerate(Types.number_image_path):
            results, loc1 = repeat_check(
                image2=cv2.imread(path, cv2.IMREAD_GRAYSCALE),
                regions=region,
                expand=[],
                threshold=0.999,
                rounds=check_round,
            )
            res1 = judgment_results(
                (results, loc1),
                is_show_true_and_none=False,
                is_show_true_and_have=False,
                is_show_false=False,
            )
            if res1:
                return index + 1

    ids = getCurrentRounds(2)
    if ids is None:
        print(config_default['text']['canCheckHowRound'])
        return False

    def handleAddOrReduce(path):
        """
        处理挑战次数增减
        Args:
            path (str): 加/减图标的图片
        Returns:
            tuple: (bool, (x, y))查询的结果，如果bool为False，那么第二个元组的值为None
        """
        return repeat_check(
            image1=cv2.imread(path, cv2.IMREAD_GRAYSCALE),
            regions=region,
            expand=[],
            rounds=3,
        )

    if ids > rounds:
        res, loc = handleAddOrReduce('image/button_black_reduce.png')
        if not res:
            res, loc = handleAddOrReduce('image/button_light_reduce.png')

        if res:
            x, y = loc
            for _ in range(ids - rounds):
                time.sleep(0.2)
                pg.click(w_left + x, w_top + y)
        else:
            print(f"{config_default['text']['canNoAddOrReduceRounds']}目标期望{rounds}，但实际为{ids}")
            return False
    elif ids < rounds:
        res, loc = handleAddOrReduce('image/button_light_add.png')
        if not res:
            res, loc = handleAddOrReduce('image/button_black_add.png')

        if res:
            x, y = loc
            for _ in range(rounds - ids):
                time.sleep(0.2)
                pg.click(w_left + x, w_top + y)
        else:
            print(f"{config_default['text']['canNoAddOrReduceRounds']}目标期望{rounds}，但实际为{ids}")
            return False
    return True


def challenge(cs_str: Types.ModeType, rounds=1):
    """
    进入副本且开始挑战
    Args:
        cs_str: 挑战的副本名
        rounds (int): 挑战次数（非拟造花萼金可忽略）
    Returns:
        bool: True如果开始挑战成功，否则返回False
    """

    def come_in(check_round=4):
        """
        进入副本（地脉次数选择）
        Args:
            check_round: 检测次数
        Returns:
            bool: True如果成功，否则返回False
        """
        results, loc = repeat_check(
            regions=region,
            expand=[],
            image1=cv2.imread('image/button_tiaozhan.png', cv2.IMREAD_GRAYSCALE),
            rounds=check_round,
            sleep=1,
        )

        if cs_str == Types.ModeType.NZHEC or cs_str == Types.ModeType.NZHEJ:
            res_set = challenge_rounds(rounds)
            if not res_set:
                print(f'没有成功设置{rounds}次挑战次数')

        return judgment_results(
            (results, loc),
            is_show_true_and_none=False,
            is_show_true_and_have=False,
            false=f"{config_default['text']['canNoFindButton']}进入挑战，无法进入挑战",
        )

    res_come_in = come_in()
    if not res_come_in:
        return False
    else:
        time.sleep(3)
        res_power = no_allow_again(0)
        if res_power:
            return False

    time.sleep(3)

    # 进入队伍选择并且开始挑战
    def start_challenge(check_round=4):
        """
        选完队伍开始挑战
        Args:
            check_round: 检测次数
        Returns:
            bool: True如果成功，否则返回False
        """
        results, loc = repeat_check(
            regions=region,
            expand=[],
            image1=cv2.imread('image/button_startTiaozhan.png', cv2.IMREAD_GRAYSCALE),
            rounds=check_round,
            sleep=1,
        )
        return judgment_results(
            (results, loc),
            is_show_true_and_none=False,
            is_show_true_and_have=False,
            false=f"{config_default['text']['canNoFindButton']}开始挑战，无法开始挑战",
        )

    res_start_challenge = start_challenge()
    if not res_start_challenge:
        return False
    else:
        return True


def no_allow_again(check_round=4):
    """
    检查是否体力不足
    Args:
        check_round (int): 检查次数
    Returns:
        bool: True为体力不足，否则为False
    """
    results, loc = repeat_check(
        regions=region,
        expand=[],
        image2=cv2.imread('image/text_no_tili.png', cv2.IMREAD_GRAYSCALE),
        rounds=check_round,
        sleep=1,
    )
    return judgment_results(
        (results, loc),
        true_and_none=config_default['text']['noPower'],
        is_show_true_and_have=False,
        false=f"{config_default['text']['canFindText']}体力不足",
    )


def judgment_results(
        results,
        is_show_true_and_none=True,
        true_and_none='默认值返回：识别成功且无坐标返回',
        is_show_true_and_have=True,
        true_and_have='默认值返回：识别成功且有坐标返回',
        is_show_false=True,
        false='默认值返回：识别失败',
        expand=None
):
    """
    处理结果(如果(bool, tuple | None)的tuple不为None，那么会执行鼠标点击)
    Args:
        results (tuple): 一个包含(bool, tuple | None)的元组
        is_show_true_and_none: 是否展示true_and_none返回内容
        true_and_none: 成功且无坐标返回的文本内容
        is_show_true_and_have: 是否展示true_and_have返回内容
        true_and_have: 成功且有坐标返回的文本内容
        is_show_false: 是否展示false返回内容
        false: 失败返回的文本内容
        expand: 再次检测的方法（例如开启自动战斗后，可再次检测是否已经开启自动战斗）
    Returns:
        bool: True为执行顺利，否则返回False
    """

    def check(val):
        res, loc = val
        if res and loc is None:
            if is_show_true_and_none:
                print(true_and_none)
            return True
        elif res and loc is not None:
            x, y = loc
            pg.click(w_left + x, w_top + y)
            time.sleep(0.5)
            if is_show_true_and_have:
                print(true_and_have)
            if expand is not None:
                return check(expand)
            return True
        elif not res:
            if is_show_false:
                print(false)
            return False

    return check(results)
