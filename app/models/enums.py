import enum
from typing import List

class InkColorStyle(str, enum.Enum):
    """绘画设色风格"""
    SHUIMO = "水墨"      # 水墨
    QINGLV = "青绿"      # 青绿
    QIANJIANG = "浅绛"   # 浅绛
    SHESE = "设色"       # 添加"设色"类型
    
    @classmethod
    def get_values(cls) -> List[str]:
        """获取所有可能的值"""
        return [e.value for e in cls]

class PaintingCategory(str, enum.Enum):
    """绘画类别"""
    PERSON = "人物"
    LANDSCAPE = "山水"
    FLOWER_BIRD = "花鸟"

class PaintingTechnique(str, enum.Enum):
    """绘画技法"""
    XIEYI = "写意"
    GONGBI = "工笔"
    BAIMIAO = "白描"
    MEIGU = "没骨"