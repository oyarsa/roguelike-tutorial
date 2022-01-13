from __future__ import annotations

import copy
import importlib.resources
import lzma
import pickle
import traceback

import tcod.image

from roguelike import colour, entity_factories, input_handlers, resources
from roguelike.engine import Engine
from roguelike.game_map import GameWorld


def new_game() -> Engine:
    map_width = 80
    map_height = 43

    room_max_size = 10
    room_min_size = 6
    max_rooms = 30

    player = copy.deepcopy(entity_factories.player)
    engine = Engine(player=player)
    engine.game_world = GameWorld(
        max_rooms=max_rooms,
        room_min_size=room_min_size,
        room_max_size=room_max_size,
        map_width=map_width,
        map_height=map_height,
        engine=engine,
    )
    engine.game_world.generate_floor()
    engine.update_fov()

    engine.log("Hello and welcome, adventure", colour.WELCOME_TEXT)
    return engine


class MainMenu(input_handlers.BaseEventHandler):
    def on_render(self, console: tcod.Console) -> None:
        with importlib.resources.path(resources, "menu_background.png") as p:
            background_image = tcod.image.load(p)[:, :, :3]
        console.draw_semigraphics(background_image, 0, 0)

        console.print(
            x=console.width // 2,
            y=console.height // 2 - 4,
            string="TOMBS OF THE ANCIENT KINGS",
            fg=colour.MENU_TITLE,
            alignment=tcod.CENTER,
        )
        console.print(
            x=console.width // 2,
            y=console.height // 2,
            string="By me",
            fg=colour.MENU_TITLE,
            alignment=tcod.CENTER,
        )

        menu_width = 24
        for i, text in enumerate(
            ["[N] Play a new game", "[C] Continue last game", "[Q] Quit"]
        ):
            console.print(
                console.width // 2,
                console.height // 2 - 2 + i,
                text.ljust(menu_width),
                fg=colour.MENU_TEXT,
                bg=colour.BLACK,
                alignment=tcod.CENTER,
                bg_blend=tcod.BKGND_ALPHA(64),
            )

    def ev_keydown(
        self, event: tcod.event.KeyDown
    ) -> input_handlers.BaseEventHandler | None:
        key = event.sym
        if key in (tcod.event.K_q, tcod.event.K_ESCAPE):
            raise SystemExit()
        elif key == tcod.event.K_c:
            try:
                return input_handlers.MainGameEventHandler(load_game("savegame.sav"))
            except FileNotFoundError:
                return input_handlers.PopupMessage(self, "No saved game to load.")
            except Exception as ex:
                traceback.print_exc()
                return input_handlers.PopupMessage(self, f"Failed to load save:\n{ex}")
        elif key == tcod.event.K_n:
            return input_handlers.MainGameEventHandler(new_game())
        return None


def load_game(filename: str) -> Engine:
    with open(filename, "rb") as f:
        engine = pickle.loads(lzma.decompress(f.read()))
    assert isinstance(engine, Engine)
    return engine
