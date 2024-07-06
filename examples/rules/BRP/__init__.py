from hrc.rule import Rule

class BRP(Rule):
    async def handle(self) -> None: ...
    
    async def rule(self) -> bool: return False