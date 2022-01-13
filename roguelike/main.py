import importlib.resources
import traceback

import tcod

from roguelike import colour, exceptions, input_handlers, resources, setup_game


def main() -> None:
    screen_width = 80
    screen_height = 50

    with importlib.resources.path(resources, "dejavu10x10_gs_tc.png") as p:
        tile_set = tcod.tileset.load_tilesheet(p, 32, 8, tcod.tileset.CHARMAP_TCOD)

    handler: input_handlers.BaseEventHandler = setup_game.MainMenu()

    with tcod.context.new_terminal(
        screen_width,
        screen_height,
        tileset=tile_set,
        title="Roguelike",
        vsync=True,
    ) as context:
        root_console = tcod.Console(screen_width, screen_height, order="F")
        try:
            while True:
                root_console.clear()
                handler.on_render(console=root_console)
                context.present(root_console)

                try:
                    for event in tcod.event.wait():
                        context.convert_event(event)
                        handler = handler.handle_events(event)
                except Exception:
                    traceback.print_exc()
                    if isinstance(handler, input_handlers.EventHandler):
                        handler.engine.log(traceback.format_exc(), colour.ERROR)
        except exceptions.QuitWithoutSaving:
            raise
        except SystemExit:
            save_game(handler, "savegame.csv")
            raise
        except BaseException:
            save_game(handler, "savegame.csv")
            raise


def save_game(handler: input_handlers.BaseEventHandler, filename: str) -> None:
    if isinstance(handler, input_handlers.EventHandler):
        handler.engine.save_as(filename)
        print("Game saved.")


if __name__ == "__main__":
    main()
