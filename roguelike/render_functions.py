from __future__ import annotations

from typing import TYPE_CHECKING

from tcod import Console

from roguelike import colour

if TYPE_CHECKING:
    from roguelike.engine import Engine
    from roguelike.game_map import GameMap


def render_bar(
    console: Console, current_value: int, max_value: int, total_width: int
) -> None:
    bar_width = int(current_value / max_value * total_width)

    console.draw_rect(x=0, y=45, width=20, height=1, ch=1, bg=colour.BAR_EMPTY)

    if bar_width > 0:
        console.draw_rect(
            x=0, y=45, width=bar_width, height=1, ch=1, bg=colour.BAR_FILLED
        )

    console.print(
        x=1, y=45, string=f"HP: {current_value}/{max_value}", fg=colour.BAR_TEXT
    )


def get_names_at(game_map: GameMap, x: int, y: int) -> str:
    if not game_map.in_bounds(x, y) or not game_map.visible[x, y]:
        return ""

    names = ", ".join(e.name for e in game_map.entities if (e.x, e.y) == (x, y))
    return names.capitalize()


def render_names_at_mouse_loc(console: Console, x: int, y: int, engine: Engine) -> None:
    mouse_x, mouse_y = engine.mouse_location
    names = get_names_at(x=mouse_x, y=mouse_y, game_map=engine.game_map)
    console.print(x=x, y=y, string=names)


def render_dungeon_level(
    console: Console, level: int, location: tuple[int, int]
) -> None:
    x, y = location
    console.print(x=x, y=y, string=f"Dungeon level: {level}")
