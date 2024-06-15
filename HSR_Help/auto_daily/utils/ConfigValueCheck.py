"""
检查配置文件合法性，合法的配置文件内容应该如下（如无特殊说明，默认0为关闭，1为开启）：
mode: 存储了一个mode对象数组，它定义了副本挑战的相关内容，mode对象的属性请往下看
waitCheck: 是否开启遗器本和历战余响本挑战成功后暂停查看遗器属性(未实装)
lazyMan: 是否开启超级懒人模式(未实装)
useFuel: 是否开启在体力不足的情况下使用燃料(1燃料=60点开拓力)(未实装)
fuelUseQuantity: 允许使用的燃料数量,可选择为大于等于0的整数(未实装)
useExtraFuel: 是否开启在体力不足的情况下使用后备开拓力(1点后备开拓力=1点开拓力)(未实装)
extraFuelUseQuantity: 允许使用的后备开拓力数量，可选择为大于等于0的整数(未实装)，每次使用的数量为60，次数由程序分配
project: 存了所有可执行的功能，project内的键值对请往下看

mode对象属性：
mode: 模式大类，接受一个GameModeTypes.py下的ModeType的值，例如侵蚀隧洞
detail: 模式小类，接受一个GameModeTypes.py下的NZHEJMode或NZHECMode或NZXYMode或QSSDMode或LZYXMode的值，例如冰风套本
round: 挑战次数，如果设为0则会一直打当前的副本，直到用完所有指定的体力（每次运行只允许有一个副本的挑战次数为0）

project下的键值对：
weiTuo: 是否执行委托派遣
email: 是否执行邮件领取
zhuZhan: 是否执行助战奖励领取
fuBen: 是否执行副本挑战
shiXun: 是否执行实训奖励领取
xunLi: 是否执行无名勋礼任务进度和奖励的领取
"""

import json

import HSR_Help.auto_daily.Types as Types


def check_config(file_name="temp"):
    """
    检查配置文件的合法性
    Returns:
        bool: True如果合法，否则返回False
    """
    with open(f'config/{file_name}.json', 'r', encoding='utf-8') as f:
        config = json.load(f)

    check_dict = {
        "暂停查看遗器属性": config["waitCheck"],
        "超级懒狗模式": config["lazyMan"],
        "使用燃料": config["useFuel"],
        "可支配的燃料数目": config["fuelUseQuantity"],
        "使用后备开拓力": config["useExtraFuel"],
        "可支配的后备开拓力数目": config["extraFuelUseQuantity"],
    }

    for item_name, item_value in check_dict.items():
        if item_value is None:
            raise ValueError(f'{item_name}不存在配置文件中！')
        if not isinstance(item_value, int):
            raise ValueError(f'{item_name}的值：{item_value}，不是一个整数！')

        if item_name in ["暂停查看遗器属性", "超级懒狗模式", "使用燃料", "使用后备开拓力"] and item_value not in [0, 1]:
            raise ValueError(f'{item_name}的值为：{item_value}，它只能在[0, 1]之间取值！')
        if check_dict["使用燃料"] == 1 and item_name == "可支配的燃料数目" and item_value <= 0:
            raise ValueError(f'{item_name}的值不能小于等于0')
        if check_dict["使用后备开拓力"] == 1 and item_name == "可支配的后备开拓力数目" and item_value <= 0:
            raise ValueError(f'{item_name}的值不能小于等于0')

    functions = config["project"]
    if functions is None:
        raise ValueError("配置文件出错，找不到键名：project")
    for key, value in functions.items():
        if key not in ['weiTuo', 'email', 'zhuZhan', 'fuBen', 'shiXun', 'xunLi']:
            raise ValueError(f'找不到键：{key}')
        if value not in [0, 1]:
            raise ValueError(f'{value}是不合法的值，它应该为[0, 1]')

    project = config["mode"]
    if project is None:
        raise IOError('无法获取配置中的项目类')

    project_len = len(project)
    for index, item in enumerate(project, start=1):
        mode = item["mode"]  # 目标副本
        detail = item["detail"]  # 副本细节
        rounds = item["round"]  # 次数

        mode1 = mode.split('.')[2]
        detail1 = detail.split('.')[2]

        modes_check(mode1, detail1, rounds, index, project_len)

    return True


def modes_check(mode: str, detail: str, rounds: int, current_times: int, total_times: int):
    """
    模式和挑战次数合法性校验
    Args:
        mode(str): 挑战模式（大类）
        detail(str): 挑战模式（小类）
        rounds(int): 挑战次数
        current_times(int): 当初循环的轮次
        total_times(int): 总循环轮次
    """
    try:
        _ = Types.ModeType[mode]
    except KeyError:
        raise ValueError(f'模式不合法，{mode}不在可选范围内')

    if rounds < 0:
        raise ValueError('不合法的挑战次数，值必须大于等于0')
    elif rounds == 0 and current_times != total_times:
        raise ValueError('不允许在最后一个副本以外设置回合数为：0')

    match mode:
        case 'NZHEJ':
            try:
                _ = Types.NZHEJMode[detail]
            except KeyError:
                raise ValueError(f'{detail}不属于拟造花萼(金)模式下')
        case 'NZHEC':
            try:
                _ = Types.NZHECMode[detail]
            except KeyError:
                raise ValueError(f'{detail}不属于拟造花萼(赤)模式下')
        case 'NZXY':
            try:
                _ = Types.NZXYMode[detail]
            except KeyError:
                raise ValueError(f'{detail}不属于凝滞虚影模式下')
        case 'QSSD':
            try:
                _ = Types.QSSDMode[detail]
            except KeyError:
                raise ValueError(f'{detail}不属于侵蚀隧洞模式下')
        case 'LZYX':
            try:
                _ = Types.LZYXMode[detail]
            except KeyError:
                raise ValueError(f'{detail}不属于历战余响模式下')
        case _:
            raise ValueError(f'{mode}不在可选范围内，你是怎么绕过前面的检测的？')
