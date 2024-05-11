import json
import HSR_Help.auto_daily.Types as Types


def check_config_value():
    """
    检查配置文件的合法性
    Returns:
        bool: True如果合法，否则返回False
    """
    with open('config/config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)

    project = config["mode"]
    if project is None:
        return False
    for item in project:
        mode = item["mode"]  # 目标副本
        detail = item["detail"]  # 副本细节
        rounds = item["round"]  # 次数

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
