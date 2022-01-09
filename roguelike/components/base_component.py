from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from roguelike.engine import Engine
    from roguelike.entity import Entity


class BaseComponent(ABC):
    entity: Entity

    @property
    def engine(self) -> Engine:
        return self.entity.game_map.engine
