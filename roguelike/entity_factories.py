from roguelike.colour import WHITE
from roguelike.components import consumable, equippable
from roguelike.components.ai import HostileEnemy
from roguelike.components.equipment import Equipment
from roguelike.components.fighter import Fighter
from roguelike.components.inventory import Inventory
from roguelike.components.level import Level
from roguelike.entity import Actor, Item

player = Actor(
    char="@",
    colour=WHITE,
    name="Player",
    ai_cls=HostileEnemy,
    fighter=Fighter(hp=30, base_defense=1, base_power=2),
    inventory=Inventory(capacity=26),
    level=Level(level_up_base=200),
    equipment=Equipment(),
)
orc = Actor(
    char="o",
    colour=(63, 127, 63),
    name="Orc",
    ai_cls=HostileEnemy,
    fighter=Fighter(hp=10, base_defense=0, base_power=3),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=35),
    equipment=Equipment(),
)
troll = Actor(
    char="t",
    colour=(0, 127, 0),
    name="Troll",
    ai_cls=HostileEnemy,
    fighter=Fighter(hp=16, base_defense=1, base_power=4),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=100),
    equipment=Equipment(),
)

health_potion = Item(
    char="!",
    colour=(127, 0, 255),
    name="Health Potion",
    consumable=consumable.HealingConsumable(amount=4),
)
lightning_scroll = Item(
    char="~",
    colour=(255, 255, 0),
    name="Lightning Scroll",
    consumable=consumable.LightningDamageConsumable(damage=20, max_range=5),
)
confusion_scroll = Item(
    char="~",
    colour=(207, 63, 255),
    name="Confusion Scroll",
    consumable=consumable.ConfusionConsumable(number_of_turns=10),
)
firebal_scroll = Item(
    char="~",
    colour=(255, 0, 0),
    name="Fireball Scroll",
    consumable=consumable.FireballDamageConsumable(damage=12, radius=3),
)

dagger = Item(
    char="/", colour=(0, 191, 255), name="Dagger", equippable=equippable.Dagger()
)
sword = Item(
    char="/", colour=(0, 191, 255), name="Sword", equippable=equippable.Sword()
)
leather_armour = Item(
    char="[",
    colour=(139, 69, 19),
    name="Leather Armour",
    equippable=equippable.LeatherArmour(),
)
chainmail = Item(
    char="[", colour=(139, 69, 19), name="Chainmail", equippable=equippable.Chainmail()
)
