import math

from hrc import Core, player_card

core = Core()


@core.event_post_processor_hook
async def auto_card(_event='T_Event'):
    g = core.session
    pc = player_card
    if g and core.session.gid and g.ac:
        if hasattr(pc.trans, '生命') or hasattr(pc.trans, '理智'):
            core.session.call("set_group_card", pc.gid, f"card#{pc.uid}", await overview_card(pc.char))


async def overview_card(pc: player_card):
    max_hp = math.floor((pc.get('CON', 0) + pc.get('SIZ', 0) / 10))
    max_san = math.floor(99 - pc.get('CM', 0))
    mp = pc.get('MP', 0)
    mp_show = " mp" + str(mp) + "/" + str(
        math.floor(pc.get('POW', 0) / 5)
    ) if mp and mp != math.floor(pc.get('POW', 0) / 5) else ""
    return pc.get('__Name', "") + " hp" + str(pc.get('HP', max_hp)) + "/" + str(max_hp) + " san" + str(pc.get('SAN', "?")) + "/" + str(max_san) + mp_show + " DEX" + str(pc.get('DEX', "?"))
