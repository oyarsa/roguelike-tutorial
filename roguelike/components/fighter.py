from __future__ import annotations

from typing import TYPE_CHECKING

from roguelike.components.base_component import BaseComponent

if TYPE_CHECKING:
    from roguelike.entity import Actor


class Fighter(BaseComponent):
    entity: Actor

    def __init__(self, hp: int, defense: int, power: int) -> None:
        self.max_hp = hp
        self._hp = hp
        self.defense = defense
        self.power = power

    def __post_init__(self) -> None:
        self._hp = self.max_hp

    @property
    def hp(self) -> int:
        return self._hp

    @hp.setter
    def hp(self, value: int) -> None:
        self._hp = max(0, min(value, self.max_hp))
        if self._hp == 0 and self.entity.ai:
            self.die()

    def die(self) -> None:
        if self.entity is self.engine.player:
            death_msg = "You died!"
        else:
            death_msg = f"{self.entity.name} is dead!"

        self.entity.char = "%"
        self.entity.colour = (191, 0, 0)
        self.entity.blocks_movement = False
        self.entity.ai = None
        self.entity.name = f"remains of {self.entity.name}"

        print(death_msg)
