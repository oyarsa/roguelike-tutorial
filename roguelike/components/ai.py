from __future__ import annotations

import random
from abc import ABC
from typing import TYPE_CHECKING, cast

import numpy as np
import tcod.path

from roguelike.actions import (
    Action,
    BumpAction,
    MeleeAction,
    MovementAction,
    WaitAction,
)
from roguelike.types import ndarray

if TYPE_CHECKING:
    from roguelike.entity import Actor


class BaseAI(Action, ABC):
    entity: Actor

    def perform(self) -> None:
        ...

    def get_path_to(self, dest_x: int, dest_y: int) -> list[tuple[int, int]]:
        cost: ndarray = np.array(self.entity.game_map.tiles["walkable"], dtype=np.int8)

        for entity in self.entity.game_map.entities:
            if entity.blocks_movement and cost[entity.x, entity.y]:
                cost[entity.x, entity.y] += 10

        graph = tcod.path.SimpleGraph(cost=cost, cardinal=2, diagonal=3)
        pathfinder = tcod.path.Pathfinder(graph)

        pathfinder.add_root((self.entity.x, self.entity.y))
        path = cast(list[list[int]], pathfinder.path_to((dest_x, dest_y))[1:].tolist())

        return [(x, y) for x, y in path]


class HostileEnemy(BaseAI):
    def __init__(self, entity: Actor):
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


class ConfusedEnemy(BaseAI):
    def __init__(self, entity: Actor, previous_ai: BaseAI | None, turns_remaining: int):
        super().__init__(entity)
        self.previous_ai = previous_ai
        self.turns_remainig = turns_remaining

    def perform(self) -> None:
        if self.turns_remainig <= 0:
            self.engine.log(f"The {self.entity.name} is no longer confused.")
            self.entity.ai = self.previous_ai
            return

        dir_x, dir_y = random.choice(
            [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
        )
        self.turns_remainig -= 1
        return BumpAction(self.entity, dir_x, dir_y).perform()
