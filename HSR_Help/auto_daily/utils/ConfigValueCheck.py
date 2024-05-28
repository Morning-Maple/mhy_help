"""
检查配置文件合法性
"""

import json

import HSR_Help.auto_daily.Types as Types


def check_config():
    """
    检查配置文件的合法性
    Returns:
        bool: True如果合法，否则返回False
    """
    with open('config/config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)

    project = config["mode"]
    if project is None:
        raise IOError('无法获取配置中的项目类')

    for item in project:
        mode = item["mode"]  # 目标副本
        detail = item["detail"]  # 副本细节
        rounds = item["round"]  # 次数

        mode1 = mode.split('.')[2]
        detail1 = detail.split('.')[2]

        modes_check(mode1, detail1, rounds)

    return True


def modes_check(mode: str, detail: str, rounds: int):
    """
    模式和挑战次数合法性校验
    Args:
        mode(str): 挑战模式（大类）
        detail(str): 挑战模式（小类）
        rounds(int): 挑战次数
    """
    try:
        _ = Types.ModeType[mode]
    except KeyError:
        raise ValueError('模式选择不在可选范围内')
    if rounds <= 0:
        raise ValueError('不合法的挑战次数')
    match mode:
        case 'NZHEJ':
            try:
                _ = Types.NZHEJMode[detail]
            except KeyError:
                raise ValueError('拟造花萼金中选择了错误的挑战地点')
        case 'NZHEC':
            try:
                _ = Types.NZHECMode[detail]
            except KeyError:
                raise ValueError('拟造花萼赤中选择了错误的挑战地点')
        case 'NZXY':
            try:
                _ = Types.NZXYMode[detail]
            except KeyError:
                raise ValueError('凝滞虚影中选择了错误的挑战地点')
        case 'QSSD':
            try:
                _ = Types.QSSDMode[detail]
            except KeyError:
                raise ValueError('侵蚀隧洞中选择了错误的挑战地点')
        case 'LZYX':
            try:
                _ = Types.LZYXMode[detail]
            except KeyError:
                raise ValueError('历战余响中选择了错误的挑战地点')
        case _:
            raise ValueError('模式选择不在可选范围内')
