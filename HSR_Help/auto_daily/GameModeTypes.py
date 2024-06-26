from enum import Enum

from newTypes import Types as T


class ModeType(Enum):
    """
    模式枚举类
    """
    NZHEJ = ('拟造花萼(金)', T.NZHEJ)
    NZHEC = ('拟造花萼(赤)', T.NZHEC)
    NZXY = ('凝滞虚影', T.NZXY)
    QSSD = ('侵蚀隧洞', T.QSSD)
    LZYX = ('历战余响', T.LZYX)

    def __init__(self, desc, types):
        self.desc = desc
        self.types = types

    @property
    def get_types(self):
        return self.types

    @property
    def get_desc(self):
        return self.desc


class NZHEJMode(Enum):
    """
    拟造花萼（金）模式枚举类
    """
    YLL6_JYCL = ('雅利洛6_经验材料', T.c_yaliluo6, T.NZHEJ_JY)
    YLL6_GZCL = ('雅利洛6_光锥材料', T.c_yaliluo6, T.NZHEJ_GZ)
    YLL6_Q = ('雅利洛6_钱', T.c_yaliluo6, T.NZHEJ_Q)
    XZ_JYCL = ('仙舟_经验材料', T.c_luofuxianzhou, T.NZHEJ_JY)
    XZ_GZCL = ('仙舟_光锥材料', T.c_luofuxianzhou, T.NZHEJ_GZ)
    XZ_Q = ('仙舟_钱', T.c_luofuxianzhou, T.NZHEJ_Q)
    PNKN_JYCL = ('匹诺康尼_经验材料', T.c_pinuokangni, T.NZHEJ_JY)
    PNKN_GZCL = ('匹诺康尼_光锥材料', T.c_pinuokangni, T.NZHEJ_GZ)
    PNKN_Q = ('匹诺康尼_钱', T.c_pinuokangni, T.NZHEJ_Q)

    def __init__(self, desc, country, types):
        self.desc = desc
        self.country = country
        self.types = types

    @property
    def get_types(self):
        return self.types

    @property
    def get_country(self):
        return self.country

    @property
    def get_desc(self):
        return self.desc


class NZHECMode(Enum):
    """
    拟造花萼（赤）模式枚举类
    """
    HM_SRCD = ('毁灭_收容舱段', T.NZHEC_HM_SRCD)
    HM_LYJ = ('毁灭_鳞渊境', T.NZHEC_HM_LYJ)
    CH_ZYCD = ('存护_支援舱段', T.NZHEC_CH_ZYCD)
    CH_KLKYSLY = ('存护_克劳克影视乐园', T.NZHEC_CH_KLKYSLY)
    XL_CJXY = ('巡猎_城郊雪原', T.NZHEC_XL_CJXY)
    XL_SLDRSHXHC = ('巡猎_苏乐达热砂海选会场', T.NZHEC_XL_SLDRSHXHC)
    FR_BYTL = ('丰饶_边缘通路', T.NZHEC_FR_BYTL)
    FR_SY = ('丰饶_绥园', T.NZHEC_FR_SY)
    ZS_MDZ = ('智识_铆钉镇', T.NZHEC_ZS_MDZ)
    ZS_PNKNDJY = ('智识_匹诺康尼大剧院', T.NZHEC_ZS_PNKNDJY)
    TX_JXJL = ('同谐_机械聚落', T.NZHEC_TX_JXJL)
    TX_BRMJD_MJ = ('同谐_白日梦酒店_梦境', T.NZHEC_TX_BRMJD_MJ)
    XW_DKQ = ('虚无_大矿区', T.NZHEC_XW_DKQ)
    XW_DDS = ('虚无_丹鼎司', T.NZHEC_XW_DDS)

    def __init__(self, desc, types):
        self.desc = desc
        self.types = types

    @property
    def get_types(self):
        return self.types

    @property
    def get_desc(self):
        return self.desc


class NZXYMode(Enum):
    """
    凝滞虚影模式枚举类
    """
    KH = ('空海之形', T.NZXY_KH)
    XF = ('巽风之形', T.NZXY_XF)
    ML = ('鸣雷之形', T.NZXY_ML)
    YH = ('炎华之形', T.NZXY_YH)
    FM = ('锋芒之形', T.NZXY_FM)
    SJ = ('霜晶之形', T.NZXY_SJ)
    HG = ('幻光之形', T.NZXY_HG)
    BL = ('冰棱之形', T.NZXY_BL)
    ZE = ('震厄之形', T.NZXY_ZE)
    YO = ('偃偶之形', T.NZXY_YO)
    NS = ('孽兽之形', T.NZXY_NS)
    FZ = ('燔灼之形', T.NZXY_FZ)
    TR = ('天人之形', T.NZXY_TR)
    YF = ('幽府之形', T.NZXY_YF)
    BN = ('冰酿之形', T.NZXY_BN)
    JZ = ('焦炙之形', T.NZXY_JZ)
    CN = ('嗔怒之形', T.NZXY_CN)
    ZS = ('职司之形', T.NZXY_ZS)

    def __init__(self, desc, types):
        self.desc = desc
        self.types = types

    @property
    def get_types(self):
        return self.types

    @property
    def get_desc(self):
        return self.desc


class QSSDMode(Enum):
    """
    侵蚀隧洞模式枚举类
    """
    SF = ('冰风套', T.QSSD_SF)
    XQ = ('物理击破套', T.QSSD_XQ)
    PB = ('治疗枪手套', T.QSSD_PB)
    RZ = ('铁卫量子套', T.QSSD_RZ)
    SS = ('圣骑士雷套', T.QSSD_SS)
    YY = ('火虚套', T.QSSD_YY)
    YS = ('莳者信使套', T.QSSD_YS)
    YM = ('大公系囚套', T.QSSD_YM)
    MQ = ('死水钟表匠套', T.QSSD_MQ)
    YQ = ('追击击破套', T.QSSD_YQ)

    def __init__(self, desc, types):
        self.desc = desc
        self.types = types

    @property
    def get_types(self):
        return self.types

    @property
    def get_desc(self):
        return self.desc


class LZYXMode(Enum):
    """
    历战余响模式枚举类
    """
    HMDKD = ('毁灭的开端', T.LZYX_HMDKD)
    HCDLM = ('寒潮的落幕', T.LZYX_HCDLM)
    BSDSS = ('不死的神实', T.LZYX_BSDSS)
    ZXDJY = ('蛀星的旧靥', T.LZYX_ZXDJY)
    CMDZL = ('尘梦的赞礼', T.LZYX_CMDZL)

    def __init__(self, desc, types):
        self.desc = desc
        self.types = types

    @property
    def get_types(self):
        return self.types

    @property
    def get_desc(self):
        return self.desc
