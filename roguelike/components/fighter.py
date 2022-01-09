from __future__ import annotations

from typing import TYPE_CHECKING

from roguelike import colour
from roguelike.components.base_component import BaseComponent
from roguelike.input_handlers import GameOverEventHandler
from roguelike.render_order import RenderOrder

if TYPE_CHECKING:
    from roguelike.entity import Actor


class Fighter(BaseComponent):
    parent: Actor

    def __init__(self, hp: int, defense: int, power: int):
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
        if self._hp == 0 and self.parent.ai:
            self.die()

    def die(self) -> None:
        if self.parent is self.engine.player:
            death_msg = "You died!"
            death_msg_colour = colour.PLAYER_DIE
            self.engine.event_handler = GameOverEventHandler(self.engine)
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

    def take_damage(self, amount: int) -> None:
        self.hp -= amount

    def heal(self, amount: int) -> int:
        if self.hp == self.max_hp:
            return 0

        new_hp = min(self.hp + amount, self.max_hp)
        recovered = new_hp - self.hp
        self.hp = new_hp
        return recovered
