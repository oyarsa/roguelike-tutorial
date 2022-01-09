from roguelike.colour import WHITE
from roguelike.components.ai import HostileEnemy
from roguelike.components.fighter import Fighter
from roguelike.entity import Actor

player = Actor(
    char="@",
    colour=WHITE,
    name="Player",
    ai_cls=HostileEnemy,
    fighter=Fighter(hp=30, defense=2, power=5),
)
orc = Actor(
    char="o",
    colour=(63, 127, 63),
    name="Orc",
    ai_cls=HostileEnemy,
    fighter=Fighter(hp=10, defense=0, power=3),
)
troll = Actor(
    char="t",
    colour=(0, 127, 0),
    name="Troll",
    ai_cls=HostileEnemy,
    fighter=Fighter(hp=16, defense=1, power=4),
)
