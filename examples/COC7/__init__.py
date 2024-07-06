import math

from hrc.core import Core
from hrc.rule import Rule, BaseRule  # noqa: F401
from hrc.dependencies import Depends

from .Character import Attributes
from .Wiki import Wiki

core = Core()


class COC7(Rule):
    
    attr: Attributes = Depends() # 必须实现一个继承自 Character.Attribute 的子类
    wiki: Wiki = Depends() # 可选实现一个 Wiki 类
    
    @core.event_postprocessor_hook
    async def auto_card(self):
        if self.session and self.session.gid and self.ac:
            if hasattr(self.pc.trans, "生命") or hasattr(self.pc.trans, "理智"):
                self.event.call_back(
                    "set_group_card", self.pc.gid, f"card#{self.pc.uid}", await self.overview_card()
                )

    async def overview_card(self):
        max_hp = math.floor((self.pc.get("CON", 0) + self.pc.get("SIZ", 0) / 10))
        max_san = math.floor(99 - self.pc.get("CM", 0))
        mp = self.pc.get("MP", 0)
        mp_show = (
            " mp" + str(mp) + "/" + str(math.floor(self.pc.get("POW", 0) / 5))
            if mp and mp != math.floor(self.pc.get("POW", 0) / 5)
            else ""
        )
        return (
            self.pc.get("__Name", "")
            + " hp"
            + str(self.pc.get("HP", max_hp))
            + "/"
            + str(max_hp)
            + " san"
            + str(self.pc.get("SAN", "?"))
            + "/"
            + str(max_san)
            + mp_show
            + " DEX"
            + str(self.pc.get("DEX", "?"))
        )