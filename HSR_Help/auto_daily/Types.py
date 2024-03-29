from enum import Enum


class ModeType(Enum):
    """
    模式枚举类
    """
    NZHEJ = ('拟造花萼(金)', 'image/text_NZHEJ.png')
    NZHEC = ('拟造花萼(赤)', 'image/text_NZHEC.png')
    NZXY = ('凝滞虚影', 'image/text_NZXY.png')
    QSSD = ('侵蚀隧洞', 'image/text_QSSD.png')
    LZYX = ('历战余响', 'image/text_LZYX.png')

    def __init__(self, desc, path):
        self.desc = desc
        self.path = path

    @property
    def get_path(self):
        return self.path


class NZHEJMode(Enum):
    """
    拟造花萼（金）模式枚举类
    """
    YLL6_JYCL = ('雅利洛6_经验材料', 'image/text_NZHEJ_JYCL.png', 'image/text_NZHEJ_YLL6.png')
    YLL6_GZCL = ('雅利洛6_光锥材料', 'image/text_NZHEJ_GZCL.png', 'image/text_NZHEJ_YLL6.png')
    YLL6_Q = ('雅利洛6_钱', 'image/text_NZHEJ_Q.png', 'text_NZHEJ_YLL6.png')
    XZ_JYCL = ('仙舟_经验材料', 'image/text_NZHEJ_JYCL.png', 'image/text_NZHEJ_XZ.png')
    XZ_GZCL = ('仙舟_光锥材料', 'image/text_NZHEJ_GZCL.png', 'image/text_NZHEJ_XZ.png')
    XZ_Q = ('仙舟_钱', 'image/text_NZHEJ_Q.png', 'image/text_NZHEJ_XZ.png')
    PNKN_JYCL = ('匹诺康尼_经验材料', 'image/text_NZHEJ_JYCL.png', 'image/text_NZHEJ_PNKN.png')
    PNKN_GZCL = ('匹诺康尼_光锥材料', 'image/text_NZHEJ_GZCL.png', 'image/text_NZHEJ_PNKN.png')
    PNKN_Q = ('匹诺康尼_钱', 'image/text_NZHEJ_Q.png', 'image/text_NZHEJ_PNKN.png')

    def __init__(self, desc, path, loc_path):
        self.desc = desc
        self.path = path
        self.loc_path = loc_path

    @property
    def get_path(self):
        return self.path

    @property
    def get_loc_path(self):
        return self.loc_path


class NZHECMode(Enum):
    """
    拟造花萼（赤）模式枚举类
    """
    HM_SRCD = ('毁灭_收容舱段', 'image/text_NZHEC_HM_SRCD.png')
    HM_LYJ = ('毁灭_鳞渊境', 'image/text_NZHEC_HM_LYJ.png')
    CH_ZYCD = ('存护_支援舱段', 'image/text_NZHEC_CH_ZYCD.png')
    XL_CJXY = ('巡猎_城郊雪原', 'image/text_NZHEC_XL_CJXY.png')
    FR_BYTL = ('丰饶_边缘通路', 'image/text_NZHEC_FR_BYTL.png')
    ZS_MDZ = ('智识_铆钉镇', 'image/text_NZHEC_ZS_MDZ.png')
    TX_JXJL = ('同谐_机械聚落', 'image/text_NZHEC_TX_JXJL.png')
    TX_BRMJD_MJ = ('同谐_白日梦酒店_梦境', 'image/text_NZHEC_TX_BRMJD_MJ.png')
    XW_DKQ = ('虚无_大矿区', 'image/text_NZHEC_XW_DKQ.png')
    XW_DDS = ('虚无_丹鼎司', 'image/text_NZHEC_XW_DDS.png')

    def __init__(self, desc, path):
        self.desc = desc
        self.path = path

    @property
    def get_path(self):
        return self.path


class NZXYMode(Enum):
    """
    凝滞虚影模式枚举类
    """
    KH = ('空海之形', 'image/text_NZXY_KH.png')
    XF = ('巽风之形', 'image/text_NZXY_XF.png')
    ML = ('鸣雷之形', 'image/text_NZXY_ML.png')
    YH = ('炎华之形', 'image/text_NZXY_YH.png')
    FM = ('锋芒之形', 'image/text_NZXY_FM.png')
    SJ = ('霜晶之形', 'image/text_NZXY_SJ.png')
    HG = ('幻光之形', 'image/text_NZXY_HG.png')
    BL = ('冰棱之形', 'image/text_NZXY_BL.png')
    ZE = ('震厄之形', 'image/text_NZXY_ZE.png')
    YO = ('偃偶之形', 'image/text_NZXY_YO.png')
    NS = ('孽兽之形', 'image/text_NZXY_NS.png')
    FZ = ('燔灼之形', 'image/text_NZXY_FZ.png')
    TR = ('天人之形', 'image/text_NZXY_TR.png')
    YF = ('幽府之形', 'image/text_NZXY_YF.png')
    BN = ('冰酿之形', 'image/text_NZXY_BN.png')
    JZ = ('焦炙之形', 'image/text_NZXY_JZ.png')

    def __init__(self, desc, path):
        self.desc = desc
        self.path = path

    @property
    def get_path(self):
        return self.path


class QSSDMode(Enum):
    """
    侵蚀隧洞模式枚举类
    """
    SF = ('冰风套', 'image/text_QSSD_SF.png')
    XQ = ('物理击破套', 'image/text_QSSD_XQ.png')
    PB = ('治疗枪手套', 'image/text_QSSD_PB.png')
    RZ = ('铁卫量子套', 'image/text_QSSD_RZ.png')
    SS = ('圣骑士雷套', 'image/text_QSSD_SS.png')
    YY = ('火虚套', 'image/text_QSSD_YY.png')
    YS = ('莳者信使套', 'image/text_QSSD_YS.png')
    YM = ('大公系囚套', 'image/text_QSSD_YM.png')
    MQ = ('死水钟表匠套', 'image/text_QSSD_MQ.png')

    def __init__(self, desc, path):
        self.desc = desc
        self.path = path

    @property
    def get_path(self):
        return self.path


class LZYXMode(Enum):
    """
    历战余响模式枚举类
    """
    HMDKD = ('毁灭的开端', 'image/text_LZYX_huimiedekaiduan.png')
    HCDLM = ('寒潮的落幕', 'image/text_LZYX_hanchaodeluomu.png')
    BSDSS = ('不死的神实', 'image/text_LZYX_busideshenshi.png')
    ZXDJY = ('蛀星的旧靥', 'image/text_LZYX_zhuxingdejiuye.png')

    def __init__(self, desc, path):
        self.desc = desc
        self.path = path

    @property
    def get_path(self):
        return self.path


number_image_path = [
    'image/10.png',
    'image/20.png',
    'image/30.png',
    'image/40.png',
    'image/50.png',
    'image/60.png'
]
