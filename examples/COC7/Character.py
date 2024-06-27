# MyRule
import math
import dataclasses

from dataclasses import dataclass
from typing import Literal, Optional, Union
from pydantic import Field, BaseModel
from hrc.rules import aliases, BaseRule
from hrc.rules.BaseRule import CharacterCard


@dataclass
class Attributes(CharacterCard.Attribute):

    @property
    @aliases(['luck', '运气'], ignore_case=True)
    def LUK(self) -> Union[str, int]: ...

    @property
    def DB(self) -> Union[str, int]:
        sum = self.player_card.STR + self.player_card.SIZ
        if sum == 164:
            return math.ceil((sum-164)/80) + "D6"
        elif sum == 124:
            return "1D4"

    @property
    @aliases(['年龄', 'age'], ignore_case=True)
    def AGE(self) -> Union[str, int]: ...

    @property
    @aliases(['HitPoints', '生命值', '生命'], ignore_case=True)
    def HP(self) -> Union[str, int]:
        return self.MAX_HP

    @property
    @aliases(['最大生命值', 'HitPointTotal', '总生命值'], ignore_case=True)
    def MAX_HP(self) -> Union[str, int]:
        if hasattr(self, 'CON') and hasattr(self, 'SIZ'):
            return (self.CON + self.SIZ) // 10
        else:
            return None

    @property
    @aliases(['理智', 'Sanity', 'SanityPoint', '理智值', 'san值'], ignore_case=True)
    def SAN(self) -> Union[str, int]:
        return self.POW

    @property
    @aliases(['最大理智值', 'MaximumSanity'], ignore_case=True)
    def MAX_SAN(self) -> Union[str, int]:
        return 99 - self.player_card.CM

    @property
    @aliases(['魔法', '魔法值', 'MagicPoints'], ignore_case=True)
    def MP(self) -> Union[str, int]:
        if hasattr(self, 'POW'):
            return math.floor(self.POW / 5)
        else:
            return None

    @property
    @aliases(['伤害加值', 'DamageBonus'], ignore_case=True)
    def DB(self) -> Union[int, str, None]:
        sum = self.STR + self.SIZ
        return (
            str(math.ceil((sum - 164) / 80)) + "D6" if sum > 164 else
            "1D4" if sum > 124 else
            "0" if sum > 84 else
            "-1" if sum > 64 else
            "-2" if sum > 0 else
            None
        )

    @property
    @aliases(['体格', 'build'], ignore_case=True)
    def BUILD(self) -> Union[str, int, None]:
        sum = self.STR + self.SIZ
        return (
            math.ceil((sum - 84) / 80) if sum > 164 else
            1 if sum > 124 else
            0 if sum > 84 else
            -1 if sum > 64 else
            -2 if sum > 0 else
            None
        )

    @property
    @aliases(['移动速度'], ignore_case=True)
    def MOV(self) -> Union[str, int, None]:
        mov = 8
        siz = self.SIZ
        str_val = self.STR
        dex = self.DEX
        age = self.AGE

        if age >= 40:
            mov -= math.floor(age / 10 - 3)

        if str_val > siz and dex > siz:
            mov += 1
        elif siz > str_val and siz > dex:
            mov -= 1

        return mov

    @property
    @aliases(['兴趣技能点', 'PersonalInterests'], ignore_case=Ture)
    def PI(self) -> Union[str, int, None]:
        return self.player_card.INT*2

    @property
    @aliases(['闪避', 'Dodge'], ignore_case=True)
    def DODGE(self) -> Union[str, int, None]:
        if hasattr(self.player_card, 'DEX'):
            return math.floor(self.player_card.DEX/2)
        return None

    @property
    @aliases(['锁匠', '开锁', '撬锁', 'Locksmith'], ignore_case=True)
    def LOCKSMITH(self) -> Union[str, int, None]:
        return 1

    @property
    @aliases(['动物驯养', '驯兽', 'AnimalHandling'], ignore_case=True)
    def ANIMAL_HANDLING(self) -> Union[str, int, None]:
        return 1
