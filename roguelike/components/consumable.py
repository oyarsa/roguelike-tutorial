from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from roguelike import actions, colour
from roguelike.components import ai
from roguelike.components.base_component import BaseComponent
from roguelike.components.inventory import Inventory
from roguelike.exceptions import ImpossibleActionError
from roguelike.input_handlers import (
    ActionOrHandler,
    AreaRangedAttackHandler,
    SingleRangedAttackHandler,
)

if TYPE_CHECKING:
    from roguelike.entity import Actor, Item


class Consumable(BaseComponent, ABC):
    parent: Item

    def get_action(self, consumer: Actor) -> ActionOrHandler | None:
        return actions.ItemAction(consumer, self.parent)

    @abstractmethod
    def activate(self, action: actions.ItemAction) -> None:
        ...

    def consume(self) -> None:
        entity = self.parent
        inventory = entity.parent
        if isinstance(inventory, Inventory):
            inventory.items.remove(entity)


class HealingConsumable(Consumable):
    def __init__(self, amount: int):
        self.amount = amount

    def activate(self, action: actions.ItemAction) -> None:
        consumer = action.entity
        recovered = consumer.fighter.heal(self.amount)

        if recovered > 0:
            self.engine.log(
                f"You consume the {self.parent.name}, and recover" f" {recovered} HP!",
                colour.HEALTH_RECOVERED,
            )
            self.consume()
        else:
            raise ImpossibleActionError("Your health is already full.")


class LightningDamageConsumable(Consumable):
    def __init__(self, damage: int, max_range: int):
        self.damage = damage
        self.max_range = max_range

    def activate(self, action: actions.ItemAction) -> None:
        consumer = action.entity
        target: Actor | None = None
        closest_distance = self.max_range + 1.0

        for actor in self.engine.game_map.actors:
            if actor is not consumer and self.parent.game_map.visible[actor.x, actor.y]:
                distance = consumer.distance(actor.x, actor.y)
                if distance < closest_distance:
                    target = actor
                    closest_distance = distance

        if target:
            self.engine.log(
                f"A lightning bolt strikes {target.name} for {self.damage} damage"
            )
            target.fighter.take_damage(self.damage)
            self.consume()
        else:
            raise ImpossibleActionError("No enemy close enough to strike")


class ConfusionConsumable(Consumable):
    def __init__(self, number_of_turns: int):
        self.number_of_turns = number_of_turns

    def get_action(self, consumer: Actor) -> SingleRangedAttackHandler:
        self.engine.log("Select a target location", colour.NEEDS_TARGET)
        return SingleRangedAttackHandler(
            self.engine,
            callback=lambda xy: actions.ItemAction(consumer, self.parent, xy),
        )

    def activate(self, action: actions.ItemAction) -> None:
        consumer = action.entity
        target = action.target_actor

        if not self.engine.game_map.visible[action.target_xy]:
            raise ImpossibleActionError("You cannot target an area you cannot see.")
        if not target:
            raise ImpossibleActionError("You must select an enemy to target.")
        if target is consumer:
            raise ImpossibleActionError("You cannot confuse yourself.")

        self.engine.log(
            f"The eyes of the {target.name} look vacant as it stumbles around",
            colour.STATUS_EFFECT_APPLIED,
        )
        target.ai = ai.ConfusedEnemy(
            entity=target, previous_ai=target.ai, turns_remaining=self.number_of_turns
        )
        self.consume()


class FireballDamageConsumable(Consumable):
    def __init__(self, damage: int, radius: int):
        self.damage = damage
        self.radius = radius

    def get_action(self, consumer: Actor) -> AreaRangedAttackHandler:
        self.engine.log("Select a target location.", colour.NEEDS_TARGET)
        return AreaRangedAttackHandler(
            self.engine,
            radius=self.radius,
            callback=lambda xy: actions.ItemAction(consumer, self.parent, xy),
        )

    def activate(self, action: actions.ItemAction) -> None:
        target_xy = action.target_xy

        if not self.engine.game_map.visible[target_xy]:
            raise ImpossibleActionError("You cannot target an are that you cannot see.")

        targets_hit = False
        for actor in self.engine.game_map.actors:
            if actor.distance(*target_xy) <= self.radius:
                self.engine.log(
                    f"The {actor.name} is engulfed in a fiery explosion "
                    f"taking {self.damage} damage"
                )
                actor.fighter.take_damage(self.damage)
                targets_hit = True

        if not targets_hit:
            raise ImpossibleActionError("There are no targets in the radius.")
        self.consume()
