from __future__ import annotations

from typing import TYPE_CHECKING, Iterable, Iterator

import numpy as np
from tcod.console import Console

from roguelike import tile_types
from roguelike.entity import Actor, Entity, Item

if TYPE_CHECKING:
    from roguelike.engine import Engine


class GameMap:
    def __init__(
        self, engine: Engine, width: int, height: int, entities: Iterable[Entity] = ()
    ) -> None:
        self.engine = engine
        self.width, self.height = width, height
        self.entities = set(entities)
        self.tiles = np.full((width, height), fill_value=tile_types.wall, order="F")

        self.visible = np.full((width, height), fill_value=False, order="F")
        self.explored = np.full((width, height), fill_value=False, order="F")
        self.downstairs_location = (0, 0)

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def render(self, console: Console) -> None:
        # noinspection PyTypeChecker
        console.tiles_rgb[: self.width, : self.height] = np.select(
            condlist=[self.visible, self.explored],
            choicelist=[self.tiles["light"], self.tiles["dark"]],
            default=tile_types.SHROUD,
        )

        entities = sorted(self.entities, key=lambda x: x.render_order.value)

        for entity in entities:
            if self.visible[entity.x, entity.y]:
                console.print(entity.x, entity.y, entity.char, fg=entity.colour)

    def get_blocking_entity_at(self, x: int, y: int) -> Entity | None:
        for e in self.entities:
            if e.blocks_movement and (e.x, e.y) == (x, y):
                return e
        return None

    @property
    def game_map(self) -> GameMap:
        return self

    @property
    def actors(self) -> Iterator[Actor]:
        yield from (e for e in self.entities if isinstance(e, Actor) and e.is_alive)

    def get_actor_at(self, x: int, y: int) -> Actor | None:
        for a in self.actors:
            if (a.x, a.y) == (x, y):
                return a
        return None

    @property
    def items(self) -> Iterator[Item]:
        yield from (e for e in self.entities if isinstance(e, Item))


class GameWorld:
    def __init__(
        self,
        *,
        engine: Engine,
        map_width: int,
        map_height: int,
        max_rooms: int,
        room_min_size: int,
        room_max_size: int,
        current_floor: int = 0,
    ):
        self.engine = engine
        self.map_width = map_width
        self.map_height = map_height
        self.max_rooms = max_rooms
        self.room_min_size = room_min_size
        self.room_max_size = room_max_size
        self.current_floor = current_floor

    def generate_floor(self) -> None:
        from roguelike.procgen import generate_dungeon

        self.current_floor += 1
        self.engine.game_map = generate_dungeon(
            max_rooms=self.max_rooms,
            room_min_size=self.room_min_size,
            room_max_size=self.room_max_size,
            map_width=self.map_width,
            map_height=self.map_height,
            engine=self.engine,
        )
