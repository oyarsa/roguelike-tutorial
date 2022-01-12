from __future__ import annotations

import math
from copy import deepcopy
from typing import TYPE_CHECKING, Type, TypeVar

from roguelike.colour import RGB, WHITE
from roguelike.components.ai import BaseAI
from roguelike.components.inventory import Inventory
from roguelike.render_order import RenderOrder

if TYPE_CHECKING:
    from roguelike.components.consumable import Consumable
    from roguelike.components.fighter import Fighter
    from roguelike.game_map import GameMap

T = TypeVar("T", bound="Entity")


class Entity:
    def __init__(
        self,
        x: int = 0,
        y: int = 0,
        char: str = "?",
        colour: RGB = WHITE,
        name: str = "<unnamed>",
        blocks_movement: bool = False,
        render_order: RenderOrder = RenderOrder.CORPSE,
        parent: GameMap | Inventory | None = None,
    ):
        self.x = x
        self.y = y
        self.char = char
        self.colour = colour
        self.name = name
        self.blocks_movement = blocks_movement
        self.render_order = render_order
        self._parent = parent

        if self._parent is not None and isinstance(self._parent, GameMap):
            self._parent.entities.add(self)

    def move(self, dx: int, dy: int) -> None:
        self.x += dx
        self.y += dy

    def __hash__(self) -> int:
        return id(self)

    def spawn(self: T, game_map: GameMap, x: int, y: int) -> T:
        clone = deepcopy(self)
        clone.x, clone.y = x, y
        clone.parent = game_map
        game_map.entities.add(clone)
        return clone

    @property
    def parent(self) -> GameMap | Inventory:
        assert self._parent is not None
        return self._parent

    @parent.setter
    def parent(self, p: GameMap | Inventory) -> None:
        self._parent = p

    @property
    def game_map(self) -> GameMap:
        return self.parent.game_map

    def place(self, x: int, y: int, game_map: GameMap | None = None) -> None:
        self.x = x
        self.y = y
        if game_map:
            if self._parent is not None and self._parent is self.game_map:
                self.game_map.entities.remove(self)
            self._parent = game_map
            game_map.entities.add(self)

    def distance(self, x: int, y: int) -> float:
        return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)


class Actor(Entity):
    def __init__(
        self,
        *,
        x: int = 0,
        y: int = 0,
        char: str = "?",
        colour: RGB = WHITE,
        name: str = "<unnamed>",
        ai_cls: Type[BaseAI],
        fighter: Fighter,
        inventory: Inventory,
    ):
        super().__init__(
            x=x,
            y=y,
            char=char,
            colour=colour,
            name=name,
            blocks_movement=True,
            render_order=RenderOrder.ACTOR,
        )
        self.ai: BaseAI | None = ai_cls(self)

        self.fighter = fighter
        self.fighter.parent = self

        self.inventory = inventory
        self.inventory.parent = self

    @property
    def is_alive(self) -> bool:
        return self.ai is not None


class Item(Entity):
    def __init__(
        self,
        *,
        consumable: Consumable,
        x: int = 0,
        y: int = 0,
        char: str = "?",
        colour: RGB = WHITE,
        name: str = "<unnamed>",
    ):
        super().__init__(
            x=x,
            y=y,
            char=char,
            colour=colour,
            name=name,
            blocks_movement=False,
            render_order=RenderOrder.ITEM,
        )
        self.consumable = consumable
        self.consumable.parent = self
