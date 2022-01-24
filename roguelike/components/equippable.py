from __future__ import annotations

from typing import TYPE_CHECKING

from roguelike.components.base_component import BaseComponent
from roguelike.equipment_types import EquipmentType

if TYPE_CHECKING:
    from roguelike.entity import Item


class Equipabble(BaseComponent):
    parent: Item

    def __init__(
        self,
        equipment_type: EquipmentType,
        power_bonus: int = 0,
        defense_bonus: int = 0,
    ):
        self.equipment_type = equipment_type
        self.power_bonus = power_bonus
        self.defense_bonus = defense_bonus


class Dagger(Equipabble):
    def __init__(self) -> None:
        super().__init__(equipment_type=EquipmentType.WEAPON, power_bonus=2)


class Sword(Equipabble):
    def __init__(self) -> None:
        super().__init__(equipment_type=EquipmentType.WEAPON, power_bonus=4)


class LeatherArmour(Equipabble):
    def __init__(self) -> None:
        super().__init__(equipment_type=EquipmentType.ARMOUR, defense_bonus=1)


class Chainmail(Equipabble):
    def __init__(self) -> None:
        super().__init__(equipment_type=EquipmentType.ARMOUR, defense_bonus=3)
