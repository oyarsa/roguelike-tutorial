from __future__ import annotations

from copy import deepcopy
from typing import TYPE_CHECKING, Type, TypeVar

from roguelike.colour import RGB, WHITE
from roguelike.components.ai import BaseAI
from roguelike.components.fighter import Fighter
from roguelike.render_order import RenderOrder

if TYPE_CHECKING:
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
        game_map: GameMap | None = None,
    ):
        self.x = x
        self.y = y
        self.char = char
        self.colour = colour
        self.name = name
        self.blocks_movement = blocks_movement
        self.render_order = render_order
        self._game_map = game_map

        if self._game_map is not None:
            self._game_map.entities.add(self)

    def move(self, dx: int, dy: int) -> None:
        self.x += dx
        self.y += dy

    def __hash__(self) -> int:
        return id(self)

    def spawn(self: T, game_map: GameMap, x: int, y: int) -> T:
        clone = deepcopy(self)
        clone.x, clone.y = x, y
        clone.game_map = game_map
        game_map.entities.add(clone)
        return clone

    def place(self, x: int, y: int, game_map: GameMap | None = None) -> None:
        self.x = x
        self.y = y
        if game_map:
            if self._game_map is not None:
                self._game_map.entities.remove(self)
            self._game_map = game_map
            game_map.entities.add(self)

    @property
    def game_map(self) -> GameMap:
        assert self._game_map is not None
        return self._game_map

    @game_map.setter
    def game_map(self, game_map: GameMap) -> None:
        self._game_map = game_map


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
        self.fighter.entity = self

    @property
    def is_alive(self) -> bool:
        return self.ai is not None
