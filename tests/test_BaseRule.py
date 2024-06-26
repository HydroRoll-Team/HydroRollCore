__rule_book__ = "BASIC ROLEPLAYING"

# General Rule Pack Standard(GRPSv1)

# 规则书剖析

# 共有的大类
# ============================
# judge role - 判定规则
# - 事件判定规则
# character card - 人物卡(属性)
# playing time* - *


# 可选的大类
# ----------------------------
# settings - 背景设定
# custom rule - 自定义规则
# - 特殊胜利手段(意外死亡、看月亮看死的等)
# expansion rule - 拓展规则
# - coc 中的伤害价值、调整
# - 装备中的盾牌
# - 药水、符文等各种各样时尚小垃圾

# 不同的大类(举例)
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#


# 规则包剖析

# 根据细类区分

# 词条 - Wiki
# 查询条目 - Query
# 规定算法 - Algorithm

# 游戏时长 - Duration
# 战斗轮、追逐轮、行动轮
# 回合
# 幕间
# 战役
# 模组

# 判定规则
# - 属性|判定 规则
# - 技能判定规则
# - 自定义类判定规则

# 人物卡
# - 属性列表*
# - 技能列表*
# - 人物塑造
# - 姓名、年龄、种族、阵营


# ==============================================

# MyRule
import hrc
from hrc.rules import BaseRule, Rules
from hrc.rules.BaseRule import CharacterCard, JudgeRule


class JudgeAttr(JudgeRule.Attribute):
    """属性判定规则"""


class JudgeCustom(JudgeRule.Custom):
    """自定义判定规则"""


class ChaAttr(CharacterCard.Attribute):
    """人物卡属性列表"""


class ChaSkill(CharacterCard.Skill):
    """人物卡技能列表"""


class ThePool(Rules[JudgeAttr, JudgeCustom]):
    """规则包[池]"""

    __config__ = 'ThePool'
    
    
 