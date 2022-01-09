from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from roguelike import actions, colour
from roguelike.components.base_component import BaseComponent
from roguelike.components.inventory import Inventory
from roguelike.exceptions import ImpossibleActionError

if TYPE_CHECKING:
    from roguelike.entity import Actor, Item


class Consumable(BaseComponent, ABC):
    parent: Item

    def get_action(self, consumer: Actor) -> actions.Action | None:
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
