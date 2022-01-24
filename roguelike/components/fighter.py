from __future__ import annotations

from typing import TYPE_CHECKING

from roguelike import colour
from roguelike.components.base_component import BaseComponent
from roguelike.render_order import RenderOrder

if TYPE_CHECKING:
    from roguelike.entity import Actor


class Fighter(BaseComponent):
    parent: Actor

    def __init__(self, hp: int, base_defense: int, base_power: int):
        self.max_hp = hp
        self._hp = hp
        self.base_defense = base_defense
        self.base_power = base_power

    def __post_init__(self) -> None:
        self._hp = self.max_hp

    @property
    def hp(self) -> int:
        return self._hp

    @hp.setter
    def hp(self, value: int) -> None:
        self._hp = max(0, min(value, self.max_hp))
        if self._hp == 0 and self.parent.ai:
            self.die()

    @property
    def defense(self) -> int:
        return self.base_defense + self.defense_bonus

    @property
    def power(self) -> int:
        return self.base_power + self.power_bonus

    @property
    def defense_bonus(self) -> int:
        if self.parent.equipment:
            return self.parent.equipment.defense_bonus
        return 0

    @property
    def power_bonus(self) -> int:
        if self.parent.equipment:
            return self.parent.equipment.power_bonus
        return 0

    def die(self) -> None:
        if self.parent is self.engine.player:
            death_msg = "You died!"
            death_msg_colour = colour.PLAYER_DIE
        else:
            death_msg = f"{self.parent.name} is dead!"
            death_msg_colour = colour.ENEMY_DIE

        self.parent.char = "%"
        self.parent.colour = (191, 0, 0)
        self.parent.blocks_movement = False
        self.parent.ai = None
        self.parent.name = f"remains of {self.parent.name}"
        self.parent.render_order = RenderOrder.CORPSE

        self.engine.log(death_msg, death_msg_colour)

        self.engine.player.level.add_xp(self.parent.level.xp_given)

    def take_damage(self, amount: int) -> None:
        self.hp -= amount

    def heal(self, amount: int) -> int:
        if self.hp == self.max_hp:
            return 0

        new_hp = min(self.hp + amount, self.max_hp)
        recovered = new_hp - self.hp
        self.hp = new_hp
        return recovered
