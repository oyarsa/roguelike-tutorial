from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from roguelike.engine import Engine
    from roguelike.entity import Actor, Entity


class Action(ABC):
    def __init__(self, entity: Actor) -> None:
        super().__init__()
        self.entity = entity

    @property
    def engine(self) -> Engine:
        return self.entity.game_map.engine

    @abstractmethod
    def perform(self) -> None:
        ...


class ActionWithDirection(Action, ABC):
    def __init__(self, entity: Actor, dx: int, dy: int) -> None:
        super().__init__(entity)
        self.dx = dx
        self.dy = dy

    @property
    def dest_xy(self) -> tuple[int, int]:
        return self.entity.x + self.dx, self.entity.y + self.dy

    @property
    def blocking_entity(self) -> Entity | None:
        return self.engine.game_map.get_blocking_entity_at(*self.dest_xy)

    @property
    def target_actor(self) -> Actor | None:
        return self.engine.game_map.get_actor_at(*self.dest_xy)


class EscapeAction(Action):
    def perform(self) -> None:
        exit()


class MovementAction(ActionWithDirection):
    def perform(self) -> None:
        dest_x, dest_y = self.dest_xy

        if not self.engine.game_map.in_bounds(dest_x, dest_y):
            return
        if not self.engine.game_map.tiles["walkable"][dest_x, dest_y]:
            return
        if self.engine.game_map.get_blocking_entity_at(dest_x, dest_y):
            return

        self.entity.move(self.dx, self.dy)


class MeleeAction(ActionWithDirection):
    def perform(self) -> None:
        target = self.target_actor
        if not target:
            return

        attack_desc = f"{self.entity.name.capitalize()} attacks {target.name} "

        damage = self.entity.fighter.power - target.fighter.defense
        if damage > 0:
            attack_desc += f"for {damage} hit points"
            target.fighter.hp -= damage
        else:
            attack_desc += "but does no damage"
        print(attack_desc)


class BumpAction(ActionWithDirection):
    def perform(self) -> None:
        if self.target_actor is not None:
            return MeleeAction(self.entity, self.dx, self.dy).perform()
        else:
            return MovementAction(self.entity, self.dx, self.dy).perform()


class WaitAction(Action):
    def perform(self) -> None:
        pass
