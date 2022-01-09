from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, cast

import numpy as np
import tcod.path

from roguelike.actions import Action, MeleeAction, MovementAction, WaitAction
from roguelike.components.base_component import BaseComponent

if TYPE_CHECKING:
    from roguelike.entity import Actor


class BaseAI(Action, BaseComponent, ABC):
    entity: Actor

    def perform(self) -> None:
        ...

    def get_path_to(self, dest_x: int, dest_y: int) -> list[tuple[int, int]]:
        cost = np.array(self.entity.game_map.tiles["walkable"], dtype=np.int8)

        for entity in self.entity.game_map.entities:
            if entity.blocks_movement and cost[entity.x, entity.y]:
                cost[entity.x, entity.y] += 10

        graph = tcod.path.SimpleGraph(cost=cost, cardinal=2, diagonal=3)
        pathfinder = tcod.path.Pathfinder(graph)

        pathfinder.add_root((self.entity.x, self.entity.y))
        path: list[list[int]] = cast(
            list, pathfinder.path_to((dest_x, dest_y))[1:].tolist()
        )

        return [(x, y) for x, y in path]


class HostileEnemy(BaseAI):
    def __init__(self, entity: Actor) -> None:
        super().__init__(entity)
        self.path: list[tuple[int, int]] = []

    def perform(self) -> None:
        target = self.engine.player
        dx = target.x - self.entity.x
        dy = target.y - self.entity.y
        dist = max(abs(dx), abs(dy))

        if self.engine.game_map.visible[self.entity.x, self.entity.y]:
            if dist <= 1:
                return MeleeAction(self.entity, dx, dy).perform()
            self.path = self.get_path_to(target.x, target.y)

        if self.path:
            dest_x, dest_y = self.path.pop(0)
            return MovementAction(
                self.entity, dest_x - self.entity.x, dest_y - self.entity.y
            ).perform()

        return WaitAction(self.entity).perform()
