import typing

RGB = typing.Tuple[int, int, int]

WHITE = (0xFF, 0xFF, 0xFF)
BLACK = (0x0, 0x0, 0x0)

PLAYER_ATK = (0xE0, 0xE0, 0xE0)
ENEMY_ATK = (0xFF, 0xC0, 0xC0)

PLAYER_DIE = (0xFF, 0x30, 0x30)
ENEMY_DIE = (0xFF, 0xA0, 0x30)

WELCOME_TXT = (0x20, 0xA0, 0xFF)

BAR_TEXT = WHITE
BAR_FILLED = (0x0, 0x60, 0x0)
BAR_EMPTY = (0x40, 0x10, 0x10)

INVALID = (0xFF, 0xFF, 0x00)
IMPOSSIBLE = (0x80, 0x80, 0x80)
ERROR = (0xFF, 0x40, 0x40)
HEALTH_RECOVERED = (0x0, 0xFF, 0x0)
