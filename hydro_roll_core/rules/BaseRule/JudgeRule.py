import dataclasses
from dataclasses import dataclass
from typing import Literal, Optional, Union
from typing_extensions import override

@dataclass
class JudgeRule(object):
    """判定规则"""
    property: type

class Custom(JudgeRule):
    ...

class Attribute(Custom):
    ...

class Skill(Custom):
    ...
