from roguelike.colour import WHITE
from roguelike.components.ai import HostileEnemy
from roguelike.components.consumable import HealingConsumable
from roguelike.components.fighter import Fighter
from roguelike.components.inventory import Inventory
from roguelike.entity import Actor, Item

player = Actor(
    char="@",
    colour=WHITE,
    name="Player",
    ai_cls=HostileEnemy,
    fighter=Fighter(hp=30, defense=2, power=5),
    inventory=Inventory(capacity=26),
)
orc = Actor(
    char="o",
    colour=(63, 127, 63),
    name="Orc",
    ai_cls=HostileEnemy,
    fighter=Fighter(hp=10, defense=0, power=3),
    inventory=Inventory(capacity=0),
)
troll = Actor(
    char="t",
    colour=(0, 127, 0),
    name="Troll",
    ai_cls=HostileEnemy,
    fighter=Fighter(hp=16, defense=1, power=4),
    inventory=Inventory(capacity=0),
)
health_potion = Item(
    char="!",
    colour=(127, 0, 255),
    name="Health Potion",
    consumable=HealingConsumable(amount=4),
)
