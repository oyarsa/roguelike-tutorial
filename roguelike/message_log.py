from __future__ import annotations

import textwrap
from collections.abc import Iterable, Reversible

import tcod

from roguelike import colour
from roguelike.colour import RGB


class Message:
    def __init__(self, text: str, fg: RGB):
        self.plain_text = text
        self.fg = fg
        self.count = 1

    @property
    def full_text(self) -> str:
        if self.count > 1:
            return f"{self.plain_text} (x{self.count})"
        return self.plain_text


class MessageLog:
    def __init__(self) -> None:
        self.messages: list[Message] = []

    def add_message(
        self, text: str, fg: RGB = colour.WHITE, *, stack: bool = True
    ) -> None:
        if stack and self.messages and text == self.messages[-1].plain_text:
            self.messages[-1].count += 1
        else:
            self.messages.append(Message(text, fg))

    def render(
        self, console: tcod.Console, x: int, y: int, width: int, height: int
    ) -> None:
        self.render_messages(console, x, y, width, height, self.messages)

    @staticmethod
    def wrap(string: str, width: int) -> Iterable[str]:
        for line in string.splitlines():
            yield from textwrap.wrap(line, width, expand_tabs=True)

    @classmethod
    def render_messages(
        cls,
        console: tcod.Console,
        x: int,
        y: int,
        width: int,
        height: int,
        messages: Reversible[Message],
    ) -> None:
        y_off = height - 1

        for msg in reversed(messages):
            for line in reversed(list(cls.wrap(msg.full_text, width))):
                console.print(x=x, y=y + y_off, string=line, fg=msg.fg)
                y_off -= 1
                if y_off < 0:
                    return
