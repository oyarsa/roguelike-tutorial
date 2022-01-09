from copy import deepcopy

import tcod

from roguelike import entity_factories
from roguelike.engine import Engine
from roguelike.procgen import generate_dungeon


def main() -> None:
    screen_width = 80
    screen_height = 50
    map_width = 80
    map_height = 45

    room_max_size = 10
    room_min_size = 6
    max_rooms = 30
    max_monsters_per_room = 2

    tile_set = tcod.tileset.load_tilesheet(
        "dejavu10x10_gs_tc.png", 32, 8, tcod.tileset.CHARMAP_TCOD
    )

    player = deepcopy(entity_factories.player)
    engine = Engine(player=player)
    engine.game_map = generate_dungeon(
        max_rooms,
        room_min_size,
        room_max_size,
        map_width,
        map_height,
        max_monsters_per_room,
        engine,
    )
    engine.update_fov()

    with tcod.context.new_terminal(
        screen_width,
        screen_height,
        tileset=tile_set,
        title="Roguelike",
        vsync=True,
    ) as context:
        root_console = tcod.Console(screen_width, screen_height, order="F")
        while True:
            engine.render(root_console, context)
            engine.event_handler.handle_events()
