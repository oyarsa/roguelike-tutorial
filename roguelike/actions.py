from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from roguelike import colour
from roguelike.exceptions import ImpossibleActionError

if TYPE_CHECKING:
    from roguelike.engine import Engine
    from roguelike.entity import Actor, Entity, Item


class Action(ABC):
    def __init__(self, entity: Actor):
        super().__init__()
        self.entity = entity

    @property
    def engine(self) -> Engine:
        return self.entity.game_map.engine

    @abstractmethod
    def perform(self) -> None:
        ...


class ActionWithDirection(Action, ABC):
    def __init__(self, entity: Actor, dx: int, dy: int):
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


class MovementAction(ActionWithDirection):
    def perform(self) -> None:
        dest_x, dest_y = self.dest_xy

        if not self.engine.game_map.in_bounds(dest_x, dest_y):
            # Out of bounds
            raise ImpossibleActionError("That way is blocked.")
        if not self.engine.game_map.tiles["walkable"][dest_x, dest_y]:
            # Blocked by a tile
            raise ImpossibleActionError("That way is blocked.")
        if self.engine.game_map.get_blocking_entity_at(dest_x, dest_y):
            # Blocked by an entity
            raise ImpossibleActionError("That way is blocked.")

        self.entity.move(self.dx, self.dy)


class MeleeAction(ActionWithDirection):
    def perform(self) -> None:
        target = self.target_actor
        if not target:
            raise ImpossibleActionError("Nothing to attack.")

        damage = self.entity.fighter.power - target.fighter.defense

        if self.entity is self.engine.player:
            atk_colour = colour.PLAYER_ATK
        else:
            atk_colour = colour.ENEMY_ATK

        attack_desc = f"{self.entity.name.capitalize()} attacks {target.name} "
        if damage > 0:
            attack_desc += f"for {damage} hit points"
            target.fighter.take_damage(damage)
        else:
            attack_desc += "but does no damage"
        self.engine.log(attack_desc, atk_colour)


class BumpAction(ActionWithDirection):
    def perform(self) -> None:
        if self.target_actor is not None:
            return MeleeAction(self.entity, self.dx, self.dy).perform()
        else:
            return MovementAction(self.entity, self.dx, self.dy).perform()


class WaitAction(Action):
    def perform(self) -> None:
        pass


class ItemAction(Action):
    def __init__(
        self, entity: Actor, item: Item, target_xy: tuple[int, int] | None = None
    ):
        super().__init__(entity)
        self.item = item
        self.target_xy = target_xy or (entity.x, entity.y)

    @property
    def target_actor(self) -> Actor | None:
        return self.engine.game_map.get_actor_at(*self.target_xy)

    def perform(self) -> None:
        self.item.consumable.activate(self)


class PickupAction(Action):
    def __init__(self, entity: Actor):
        super().__init__(entity)

    def perform(self) -> None:
        actor_x, actor_y = self.entity.x, self.entity.y
        inventory = self.entity.inventory

        for item in self.engine.game_map.items:
            if (actor_x, actor_y) == (item.x, item.y):
                if len(inventory.items) >= inventory.capacity:
                    raise ImpossibleActionError("Your inventory is full.")

                self.engine.game_map.entities.remove(item)
                item.parent = inventory
                inventory.items.append(item)

                self.engine.log(f"You picked up {item.name}.")
                return

        raise ImpossibleActionError("There is nothing here to pick up.")


class DropItem(ItemAction):
    def perform(self) -> None:
        self.entity.inventory.drop(self.item)
