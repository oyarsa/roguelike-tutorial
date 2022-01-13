from __future__ import annotations

import random
from typing import Iterator

import tcod

from roguelike import entity_factories, tile_types
from roguelike.engine import Engine
from roguelike.entity import Entity
from roguelike.game_map import GameMap

max_items_by_floor = [
    (1, 1),
    (4, 2),
]
max_monsters_by_floor = [
    (1, 2),
    (4, 3),
    (6, 5),
]

item_chances: dict[int, list[tuple[Entity, int]]] = {
    0: [(entity_factories.health_potion, 35)],
    2: [(entity_factories.confusion_scroll, 10)],
    4: [(entity_factories.lightning_scroll, 25)],
    6: [(entity_factories.firebal_scroll, 25)],
}
enemy_chances: dict[int, list[tuple[Entity, int]]] = {
    0: [(entity_factories.orc, 80)],
    3: [(entity_factories.troll, 15)],
    5: [(entity_factories.troll, 30)],
    7: [(entity_factories.troll, 60)],
}


def get_max_value_for_floor(max_val_by_floor: list[tuple[int, int]], floor: int) -> int:
    current = 0
    for floor_min, val in max_val_by_floor:
        if floor_min > floor:
            break
        current = val
    return current


def get_rand_entity(
    floor_weighted_chances: dict[int, list[tuple[Entity, int]]],
    number_of_entities: int,
    floor: int,
) -> list[Entity]:
    entity_weighted_chances = {}

    for key, values in floor_weighted_chances.items():
        if key > floor:
            break
        for entity, weight in values:
            entity_weighted_chances[entity] = weight

    entities = list(entity_weighted_chances.keys())
    entity_weights = list(entity_weighted_chances.values())

    chosen_entities = random.choices(
        entities, weights=entity_weights, k=number_of_entities
    )
    return chosen_entities


class RectangularRoom:
    def __init__(self, x: int, y: int, width: int, height: int):
        self.x1 = x
        self.y1 = y
        self.x2 = x + width
        self.y2 = y + height

    @property
    def center(self) -> tuple[int, int]:
        center_x = (self.x1 + self.x2) // 2
        center_y = (self.y1 + self.y2) // 2
        return center_x, center_y

    @property
    def inner(self) -> tuple[slice, slice]:
        """Return innear area of this room as a 2D array index."""
        return slice(self.x1 + 1, self.x2), slice(self.y1 + 1, self.y2)

    def intersects(self, other: RectangularRoom) -> bool:
        return (
            self.x1 <= other.x2
            and self.x2 >= other.x1
            and self.y1 <= other.y2
            and self.y2 <= other.y1
        )


def generate_dungeon(
    max_rooms: int,
    room_min_size: int,
    room_max_size: int,
    map_width: int,
    map_height: int,
    engine: Engine,
) -> GameMap:
    player = engine.player
    dungeon = GameMap(engine, map_width, map_height, entities=[player])
    rooms: list[RectangularRoom] = []

    centre_of_last_room = (0, 0)

    for _ in range(max_rooms):
        room_width = random.randint(room_min_size, room_max_size)
        room_height = random.randint(room_min_size, room_max_size)

        x = random.randint(0, dungeon.width - room_width - 1)
        y = random.randint(0, dungeon.height - room_height - 1)
        new_room = RectangularRoom(x, y, room_width, room_height)
        if any(new_room.intersects(other) for other in rooms):
            continue

        dungeon.tiles[new_room.inner] = tile_types.floor

        if len(rooms) == 0:
            player.place(*new_room.center, game_map=dungeon)
        else:
            for x, y in tunnel_between(rooms[-1].center, new_room.center):
                dungeon.tiles[x, y] = tile_types.floor
            centre_of_last_room = new_room.center

        place_entities(new_room, dungeon, engine.game_world.current_floor)

        dungeon.tiles[centre_of_last_room] = tile_types.downstairs
        dungeon.downstairs_location = centre_of_last_room

        rooms.append(new_room)

    return dungeon


def tunnel_between(
    start: tuple[int, int], end: tuple[int, int]
) -> Iterator[tuple[int, int]]:
    x1, y1 = start
    x2, y2 = end

    if random.random() < 0.5:
        corner_x, corner_y = x2, y1
    else:
        corner_x, corner_y = x1, y2

    # noinspection PyTypeChecker
    for x, y in tcod.los.bresenham((x1, y1), (corner_x, corner_y)).tolist():
        yield x, y
    # noinspection PyTypeChecker
    for x, y in tcod.los.bresenham((corner_x, corner_y), (x2, y2)).tolist():
        yield x, y


def place_entities(room: RectangularRoom, dungeon: GameMap, floor_number: int) -> None:
    n_monsters = random.randint(
        0, get_max_value_for_floor(max_monsters_by_floor, floor_number)
    )
    n_items = random.randint(
        0, get_max_value_for_floor(max_items_by_floor, floor_number)
    )
    monsters: list[Entity] = get_rand_entity(enemy_chances, n_monsters, floor_number)
    items: list[Entity] = get_rand_entity(item_chances, n_items, floor_number)

    for entity in monsters + items:
        x = random.randint(room.x1 + 1, room.x2 - 1)
        y = random.randint(room.y1 + 1, room.y2 - 1)

        if not any((e.x, e.y) == (x, y) for e in dungeon.entities):
            entity.spawn(dungeon, x, y)
