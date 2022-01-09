from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from roguelike.engine import Engine
    from roguelike.entity import Entity
    from roguelike.game_map import GameMap


class BaseComponent(ABC):
    parent: Entity

    @property
    def game_map(self) -> GameMap:
        return self.parent.game_map

    @property
    def engine(self) -> Engine:
        return self.game_map.engine
