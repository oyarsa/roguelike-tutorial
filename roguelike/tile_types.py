import numpy as np

from roguelike.colour import RGB, WHITE
from roguelike.types import ndarray

graphic_dt = np.dtype(
    [
        ("ch", np.int32),  # unicode codepoint
        ("fg", "3B"),  # 3 bytes for RGB colours
        ("bg", "3B"),
    ]
)

tile_dt = np.dtype(
    [
        ("walkable", np.bool_),
        ("transparent", np.bool_),
        ("dark", graphic_dt),
        ("light", graphic_dt),
    ]
)


def new_tile(
    *,
    walkable: int,
    transparent: int,
    dark: tuple[int, RGB, RGB],
    light: tuple[int, RGB, RGB]
) -> ndarray:
    return np.array((walkable, transparent, dark, light), dtype=tile_dt)


SPACE = ord(" ")
SHROUD: ndarray = np.array((ord(" "), WHITE, (0, 0, 0)), dtype=graphic_dt)
floor = new_tile(
    walkable=True,
    transparent=True,
    dark=(SPACE, WHITE, (50, 50, 150)),
    light=(SPACE, WHITE, (200, 180, 50)),
)
wall = new_tile(
    walkable=False,
    transparent=False,
    dark=(SPACE, WHITE, (0, 0, 100)),
    light=(SPACE, WHITE, (130, 110, 50)),
)
