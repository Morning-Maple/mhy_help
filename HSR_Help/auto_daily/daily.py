import json
import time
from datetime import datetime, timedelta
from logging import Logger
from typing import Any

import cv2
import pyautogui as pg
import pygetwindow as gw
from pygetwindow import Win32Window

import Types
from config.logger import LoggerLevel
from utils.utils import ImageOperation, repeat_check, listen_for_double_space
from utils.ConfigValueCheck import check_config_value

logger: Logger

w_left, w_top, w_width, w_height = 0, 0, 0, 0
region = (0, 0, 0, 0)
# 获取游戏窗口
game_window = list[Win32Window]

config_default: Any
config: Any


def get_config():
    """
    读取配置文件
    """
    global config_default, config
    with open('config/default_config.json', 'r', encoding='utf-8') as f1:
        config_default = json.load(f1)
    with open('config/config.json', 'r', encoding='utf-8') as f2:
        config = json.load(f2)


def set_logger(log):
    """获取唯一的日志对象"""
    global logger
    logger = log


def compute_resolution():
    """
    计算因分辨率而导致鼠标在X轴上的偏差
    """
    return config_default["coefficient"]["k"] * w_width + config_default["coefficient"]["b"]


def check_window():
    """
    初始化部分变量数据
    Returns:
        bool: 如果成功获取窗体并设置相关参数，返回True，否则找不到窗体返回False
    """
    global w_left, w_top, w_width, w_height, region, game_window
    game_window = gw.getWindowsWithTitle('崩坏：星穹铁道')

    if game_window:
        game_window = game_window[0]
    else:
        return False

    if not game_window.isActive:
        # 防止最小化，同时激活窗口
        game_window.restore()
        game_window.activate()
        # 获取窗口的位置信息
        w_left, w_top, w_width, w_height = game_window.left, game_window.top, game_window.width, game_window.height
        region = (w_left, w_top, w_width, w_height)
    return True


def auto_do_daily():
    global w_left, w_top, w_width, w_height, region, game_window

    logger.info(">>>> 开始")
    get_config()
    c_res = check_window()
    if not c_res:
        logger.error('未能识别到游戏窗口！执行失败')
        return False
    time.sleep(0.5)  # 等待窗口激活
    time.sleep(2)

    pg.press('m')
    time.sleep(3)
    # 委托派遣
    if config["project"]["wt"] == 1:
        time.sleep(2)
        res = wt()
        if not res:
            logger.warning('委托执行异常结束')
            return False

    # 副本挑战
    if config["project"]["fb"] == 1:
        res = fb_challenge()
        if not res:
            logger.warning('副本挑战执行异常结束')
            return False

    # 无名勋礼
    if config["project"]["xl"] == 1:
        res = xl()
        if not res:
            logger.warning('无名勋礼执行异常结束')
            return False

    # 杂项
    if config["project"]["sx_q_email"] == 1:
        res = get_sx_email_q()
        if not res:
            logger.warning('实训、助战奖励、邮件领取执行异常结束')
            return False

    logger.info('全部项目已完成！')
    logger.info('======== 分割线 ========')
    return True


def fb_challenge():
    """
    副本挑战
    Returns:
        bool: True为挑战成功，否则为False
    """
    project = config["mode"]
    if project is None:
        project = []
    for item in project:
        time.sleep(4)
        res = default_way()
        if not res:
            logger.warning('执行异常结束')
            return False

        mode = item["mode"]  # 目标副本
        detail = item["detail"]  # 副本细节
        rounds = item["round"]  # 次数

        res = check_config_value()
        if not res:
            logger.error(config_default['text']['settingError'])
            return False
        mode = getattr(getattr(Types, mode.split('.')[1]), mode.split('.')[2])
        detail = getattr(getattr(Types, detail.split('.')[1]), detail.split('.')[2])

        res = choose_mode(mode)
        if not res:
            return False

        # 首次挑战
        time.sleep(3)
        res = choose_mode_detail(detail, mode)

        if not res:
            return False
        res = watch_battle()
        if not res:
            return False
        elif mode == Types.ModeType.QSSD and config['waitCheck'] == 1:
            logger.info('需要进行查看，如果查看完毕请双击空格')
            listen_for_double_space()
            logger.info('查看完毕，继续')

        # 重复挑战
        for _ in range(rounds - 1):
            res = battle_again()
            if not res:
                return False

            res = watch_battle(first=False)
            if not res:
                return False
            else:
                if mode == Types.ModeType.QSSD and config['waitCheck'] == 1:
                    logger.info('阻塞，进行查看')
                    listen_for_double_space()
                    logger.info('查看完毕，继续')
                continue

        # 最后要退出副本然后再执行下一步
        results, loc = repeat_check(
            image1=cv2.imread('image/button_leave_challenge.png', cv2.IMREAD_GRAYSCALE),
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

        if not res:
            logger.warning('无法离开副本')
            return False
        continue

    return True


def watch_battle(t=6, first=True):
    """
    战斗监测
    Args:
        t: 副本挑战限制时间（分钟）
        first (bool): 默认为True，此时会检测二倍速和自动战斗，如果为False，则不检测自动战斗和二倍速
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

    if first:
        time.sleep(1)
        results, loc = check_double_speed()
        res = judgment_results(
            (results, loc),
            true_and_none=config_default['text']['doubleSpeedOpening'],
            true_and_have=config_default['text']['successOpenDoubleSpeed'],
            false=config_default['text']['canNotOpenDoubleSpeed'],
            expand=check_double_speed()
        )
        if not res:
            logger.error(config_default['text']['error'])

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

    if first:
        time.sleep(1)
        results, loc = check_auto_battle()
        res = judgment_results(
            (results, loc),
            true_and_none=config_default['text']['autoBattleOpening'],
            true_and_have=config_default['text']['successOpenAutoBattle'],
            false=config_default['text']['canNotOpenAutoBattle'],
            expand=check_double_speed()
        )
        if not res:
            logger.error(config_default['text']['error'])
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
            image2=cv2.imread('image/text_challengeSuccess.png', cv2.IMREAD_GRAYSCALE),
            regions=region,
            expand=[ImageOperation.CANNY],
            rounds=1,
            threshold=0.8
        )
        if is_finsh:
            return True
        elif datetime.now() - changeTime > timedelta(minutes=times):
            logger.error(f'{config_default["text"]["timeOutInBattle"]}{times}分钟')
        else:
            time.sleep(5)
            return check_finish()

    return check_finish(t)


def battle_again():
    """
    再次挑战
    Returns:
        bool: True为成功点击再次挑战，否则返回False
    """
    time.sleep(3)
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
        time.sleep(3)
        isAllow = no_allow_again(2)
        if isAllow:
            logger.error(config_default['text']['noPower'])
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
    time.sleep(3)
    pg.press('esc')
    time.sleep(3)

    # 实训领取
    def get_sx():
        """
        领取实训奖励
        """
        results, loc = repeat_check(
            image1=cv2.imread('image/button_zhinan.png', cv2.IMREAD_GRAYSCALE),
            regions=region,
            expand=[ImageOperation.CANNY],
            rounds=4,
            sleep=1,
            threshold=0.85,
        )
        res1 = judgment_results(
            (results, loc),
            is_show_true_and_none=False,
            is_show_true_and_have=False,
            false=f"{config_default['text']['canNoFindButton']}{'指南'}",
        )
        if not res1:
            return False, None

        time.sleep(3)
        results, loc = repeat_check(
            image1=cv2.imread('image/button_meirishixun.png', cv2.IMREAD_GRAYSCALE),
            regions=region,
            expand=[ImageOperation.CANNY],
            rounds=4,
            sleep=1,
        )
        res1 = judgment_results(
            (results, loc),
            is_show_true_and_none=False,
            is_show_true_and_have=False,
            false=f"{config_default['text']['canNoFindButton']}{'每日实训'}",
        )
        if not res1:
            return False, None

        rounds = 0
        while True:
            if rounds > 2:
                break
            time.sleep(3)
            results, loc = repeat_check(
                image1=cv2.imread('image/button_get.png', cv2.IMREAD_GRAYSCALE),
                regions=region,
                expand=[],
                rounds=2,
                sleep=1,
                threshold=0.8
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
            else:
                rounds += 1
                continue

        time.sleep(3)
        results, loc = repeat_check(
            image1=cv2.imread('image/button_shixun.png', cv2.IMREAD_GRAYSCALE),
            regions=region,
            image2=cv2.imread('image/text_sx_benrihuoyueduyiman.png', cv2.IMREAD_GRAYSCALE),
            expand=[],
            rounds=4,
            sleep=1,
        )
        re1 = judgment_results(
            (results, loc),
            true_and_none=config_default['text']['shiXunIsFull'],
            true_and_have=config_default['text']['successGetShiXun'],
            false=config_default['text']['extraShiXunTip'],
        )
        # 如果没有坐标，说明没有领取奖励，也就说只需要一次ESC
        if loc is None:
            return re1, True
        else:
            return re1, False

    res_sx1, res_sx2 = get_sx()
    if not res_sx1:
        return False
    else:
        time.sleep(1)
        pg.press('esc')
    if not res_sx2:
        time.sleep(3)
        pg.press('esc')

    time.sleep(3)

    def get_email():
        """
        邮件领取
        """
        results, loc = repeat_check(
            image1=cv2.imread('image/button_email.png', cv2.IMREAD_GRAYSCALE),
            regions=region,
            expand=[ImageOperation.CANNY],
            rounds=4,
            sleep=1,
            threshold=0.8
        )
        res1 = judgment_results(
            (results, loc),
            is_show_true_and_none=False,
            is_show_true_and_have=False,
            false=f"{config_default['text']['canNoFindButton']}{'邮件'}",
        )
        if not res1:
            return False, None

        time.sleep(3)
        results, loc = repeat_check(
            image1=cv2.imread('image/button_all_get.png', cv2.IMREAD_GRAYSCALE),
            regions=region,
            expand=[],
            rounds=4,
            sleep=1,
        )
        res = judgment_results(
            (results, loc),
            is_show_true_and_none=False,
            true_and_have=config_default['text']['successGetEmail'],
            false=config_default['text']['noEmailCanGet'],
        )
        return True, res

    res_email1, res_email2 = get_email()
    if not res_email1:
        return False
    else:
        time.sleep(1)
        pg.press('esc')
    # 没有邮件需要领取的时候，只需一次ESC
    if res_email2:
        time.sleep(1)
        pg.press('esc')

    time.sleep(3)

    def get_q():
        """
        领取助战奖励
        """
        results, loc = repeat_check(
            image1=cv2.imread('image/button_q.png', cv2.IMREAD_GRAYSCALE),
            regions=region,
            expand=[ImageOperation.CANNY],
            rounds=4,
            sleep=1,
            threshold=0.71,
        )
        res1 = judgment_results(
            (results, loc),
            is_show_true_and_none=False,
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
        judgment_results(
            (results, loc),
            is_show_true_and_none=False,
            true_and_have=config_default['text']['successGetMoney'],
            false=config_default['text']['noMoneyGet'],
        )
        return True

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
        image1=cv2.imread('image/button_weituo.png', cv2.IMREAD_GRAYSCALE),
        regions=region,
        expand=[],
        rounds=4,
        sleep=1,
        threshold=0.8,
    )
    res = judgment_results(
        (results, loc),
        is_show_true_and_none=False,
        is_show_true_and_have=False,
        false=f"{config_default['text']['canNoFindButton']}委托",
    )
    if not res:
        return False
    elif loc is None:
        pg.press('esc')
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
        false=config_default['text']['noWeiTuoCanHandle'],
    )
    if not res:
        time.sleep(2)
        pg.press('esc')
        time.sleep(2)
        pg.press('esc')
        return True

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
    time.sleep(3)
    pg.press('esc')
    time.sleep(3)

    results, loc = repeat_check(
        image1=cv2.imread('image/button_xl.png', cv2.IMREAD_GRAYSCALE),
        regions=region,
        expand=[],
        rounds=4,
        sleep=1,
        threshold=0.8,
    )
    res = judgment_results(
        (results, loc),
        is_show_true_and_none=False,
        is_show_true_and_have=False,
        false=f"{config_default['text']['canNoFindButton']}无名勋礼",
    )
    if not res:
        return False

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
        time.sleep(3)
        # 无名勋礼的任务需要领取，领取完毕跳回奖励页面
        results1, loc1 = repeat_check(
            image1=cv2.imread('image/button_one_click_get_1.png', cv2.IMREAD_GRAYSCALE),
            regions=region,
            expand=[],
            rounds=4,
            sleep=1,
            threshold=0.7
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
            time.sleep(2)
            pg.press('esc')
            time.sleep(2)
            pg.press('esc')
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
        is_show_true_and_none=False,
        true_and_have=config_default['text']['successGetXunLiJiangLi'],
        false=config_default['text']['noXunLiJiangLiGet'],
    )
    time.sleep(2)
    pg.press('esc')
    time.sleep(2)
    pg.press('esc')
    if res:
        time.sleep(2)
        pg.press('esc')
    return True


def default_way():
    """
    立即回到生存索引页面
    Returns:
        bool: True如果执行成功，否则返回False
    """
    time.sleep(2)
    pg.press(config['button'])
    time.sleep(2)

    results, loc = repeat_check(
        regions=region,
        expand=[ImageOperation.CANNY],
        image1=cv2.imread('image/button_shengcunsuoyin.png', cv2.IMREAD_GRAYSCALE),
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

    check_times = 6

    def check_mode(check_round=0):
        """
        模式选择
        Returns:
            bool: True为成功，其余为失败
        """
        if check_round > check_times:
            return None

        results, loc = repeat_check(
            regions=region,
            expand=[],
            image1=image,
            rounds=4,
            sleep=1,
            threshold=0.85
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
        logger.error(config_default['text']['chooseModeFail'])
        return False


def choose_mode_detail(
        detail_type: Types.LZYXMode | Types.QSSDMode | Types.NZXYMode | Types.NZHECMode | Types.NZHEJMode,
        cs_str: Types.ModeType,
):
    """
    选择详细模式并且传送过去，到查看副本详情模式(点开始挑战就进入到选队伍页面)
    Args:
        detail_type: 详细的模式
        cs_str: 模式
    Returns:
        bool: True为开始挑战成功，否则返回False
    """
    pg.moveTo(w_left + config_default['rightSide']['x'], w_top + config_default['rightSide']['y'], duration=0.1)

    check_window()

    check_times = 8
    if cs_str == Types.ModeType.NZHEC or cs_str == Types.ModeType.NZXY or cs_str == Types.ModeType.QSSD:
        check_times = 16

    # 副本传送实现
    def teleport_challenge(check_round=0):
        """
        副本选择（普通）
        Returns:
            bool: True为成功，其余为失败
        """
        if check_round > check_times:
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
            pg.moveTo(w_left + config_default['rightSide']['x'], w_top + config_default['rightSide']['y'])
            for _ in range(10):
                pg.scroll(-600)
            time.sleep(2)
            return teleport_challenge(check_round + 1)

    location = teleport_challenge(0)

    if location:
        x, y = location
        pg.click(w_left + x + config_default[cs_str.name]['x'], w_top + y + config_default[cs_str.name]['y'])
        time.sleep(8)
    else:
        logger.error(config_default['text']['canNoTeleport'])
        return False

    ################

    return challenge()


def challenge():
    """
    进入副本，选人页面，开始挑战
    Returns:
        bool: True如果开始挑战成功，否则返回False
    """

    def come_in(check_round=4):
        """
        进入副本，到选人页面
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
        res_power = no_allow_again(2)
        if res_power:
            return False

    time.sleep(3)

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
    time.sleep(3)
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
        is_show_false=False,
    )


def judgment_results(
        results,
        is_show_true_and_none=True,
        true_and_none_logger_level=LoggerLevel.INFO,
        true_and_none='默认值返回：识别成功且无坐标返回',
        is_show_true_and_have=True,
        true_and_have_logger_level=LoggerLevel.INFO,
        true_and_have='默认值返回：识别成功且有坐标返回',
        is_show_false=True,
        false_logger_level=LoggerLevel.INFO,
        false='默认值返回：识别失败',
        expand=None
):
    """
    处理结果(如果(bool, tuple | None)的tuple不为None，那么会执行鼠标点击)
    Args:
        results (tuple): 一个包含(bool, tuple | None)的元组
        is_show_true_and_none: 是否展示true_and_none返回内容
        true_and_none_logger_level: 日志输出级别
        true_and_none: 成功且无坐标返回的文本内容
        is_show_true_and_have: 是否展示true_and_have返回内容
        true_and_have_logger_level: 日志输出级别
        true_and_have: 成功且有坐标返回的文本内容
        is_show_false: 是否展示false返回内容
        false_logger_level: 日志输出级别
        false: 失败返回的文本内容
        expand: 再次检测的方法（例如开启自动战斗后，可再次检测是否已经开启自动战斗）
    Returns:
        bool: True为执行顺利，否则返回False
    """

    def log_print(val: LoggerLevel, desc: str):
        match val:
            case LoggerLevel.DEBUG:
                logger.debug(desc)
            case LoggerLevel.INFO:
                logger.info(desc)
            case LoggerLevel.WARNING:
                logger.warning(desc)
            case LoggerLevel.ERROR:
                logger.error(desc)
            case LoggerLevel.CRITICAL:
                logger.critical(desc)

    is_first = True  # 防止expand有值的时候导致无限迭代

    def check(val):
        nonlocal is_first
        res, loc = val
        if res and loc is None:
            if is_show_true_and_none:
                log_print(true_and_none_logger_level, true_and_none)
            return True
        elif res and loc is not None:
            if not is_first:
                return True
            x, y = loc
            pg.click(w_left + x, w_top + y)
            time.sleep(0.5)
            if is_show_true_and_have:
                log_print(true_and_have_logger_level, true_and_have)
            if expand is not None and is_first:
                is_first = False
                return check(expand)
            return True
        elif not res:
            if is_show_false:
                log_print(false_logger_level, false)
            return False

    return check(results)
