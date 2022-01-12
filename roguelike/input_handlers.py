from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Callable, Optional

import tcod.event

from roguelike import colour
from roguelike.actions import Action, BumpAction, DropItem, PickupAction, WaitAction
from roguelike.entity import Item
from roguelike.exceptions import ImpossibleActionError

if TYPE_CHECKING:
    from roguelike.engine import Engine

MOVE_KEYS = {
    # Arrow keys.
    tcod.event.K_UP: (0, -1),
    tcod.event.K_DOWN: (0, 1),
    tcod.event.K_LEFT: (-1, 0),
    tcod.event.K_RIGHT: (1, 0),
    tcod.event.K_HOME: (-1, -1),
    tcod.event.K_END: (-1, 1),
    tcod.event.K_PAGEUP: (1, -1),
    tcod.event.K_PAGEDOWN: (1, 1),
    # Numpad keys.
    tcod.event.K_KP_1: (-1, 1),
    tcod.event.K_KP_2: (0, 1),
    tcod.event.K_KP_3: (1, 1),
    tcod.event.K_KP_4: (-1, 0),
    tcod.event.K_KP_6: (1, 0),
    tcod.event.K_KP_7: (-1, -1),
    tcod.event.K_KP_8: (0, -1),
    tcod.event.K_KP_9: (1, -1),
    # Vi keys.
    tcod.event.K_h: (-1, 0),
    tcod.event.K_j: (0, 1),
    tcod.event.K_k: (0, -1),
    tcod.event.K_l: (1, 0),
    tcod.event.K_y: (-1, -1),
    tcod.event.K_u: (1, -1),
    tcod.event.K_b: (-1, 1),
    tcod.event.K_n: (1, 1),
}

WAIT_KEYS = {
    tcod.event.K_PERIOD,
    tcod.event.K_KP_5,
    tcod.event.K_CLEAR,
}

CURSOR_Y_KEYS = {
    tcod.event.K_UP: -1,
    tcod.event.K_DOWN: 1,
    tcod.event.K_PAGEUP: -10,
    tcod.event.K_PAGEDOWN: 10,
}

CONFIRM_KEYS = {
    tcod.event.K_KP_ENTER,
    tcod.event.K_RETURN,
}


class EventHandler(tcod.event.EventDispatch[Action], ABC):
    def __init__(self, engine: Engine):
        self.engine = engine

    def handle_events(self, event: tcod.event.Event) -> None:
        self.handle_action(self.dispatch(event))

    def ev_mousemotion(self, event: tcod.event.MouseMotion) -> Action | None:
        x, y = event.tile
        if self.engine.game_map.in_bounds(x, y):
            self.engine.mouse_location = (x, y)
        return None

    def ev_quit(self, event: tcod.event.Quit) -> Action | None:
        raise SystemExit()

    def on_render(self, console: tcod.Console) -> None:
        self.engine.render(console)

    def handle_action(self, action: Action | None) -> bool:
        if action is None:
            return False

        try:
            action.perform()
        except ImpossibleActionError as ex:
            self.engine.log(ex.args[0], colour.IMPOSSIBLE)
            return False

        self.engine.handle_enemy_turns()
        self.engine.update_fov()
        return True


class MainGameEventHandler(EventHandler):
    def ev_keydown(self, event: tcod.event.KeyDown) -> Action | None:
        action: Action | None = None
        key = event.sym
        player = self.engine.player

        if key in MOVE_KEYS:
            dx, dy = MOVE_KEYS[key]
            action = BumpAction(player, dx, dy)
        elif key in WAIT_KEYS:
            action = WaitAction(player)
        elif key == tcod.event.K_ESCAPE:
            raise SystemExit()
        elif key == tcod.event.K_v:
            self.engine.event_handler = HistoryViewer(self.engine)
        elif key == tcod.event.K_g:
            action = PickupAction(player)
        elif key == tcod.event.K_i:
            self.engine.event_handler = InventoryActivateHandler(self.engine)
        elif key == tcod.event.K_d:
            self.engine.event_handler = InventoryDropHandler(self.engine)
        elif key == tcod.event.K_SLASH:
            self.engine.event_handler = LookHandler(self.engine)

        return action


class GameOverEventHandler(EventHandler):
    def ev_keydown(self, event: tcod.event.KeyDown) -> Action | None:
        if event.sym == tcod.event.K_ESCAPE:
            raise SystemExit()
        return None


class HistoryViewer(EventHandler):
    def __init__(self, engine: Engine):
        super().__init__(engine)
        self.log_length = len(engine.message_log.messages)
        self.cursor = self.log_length - 1

    def on_render(self, console: tcod.Console) -> None:
        super().on_render(console)
        log_console = tcod.Console(console.width - 6, console.height - 6)

        log_console.draw_frame(0, 0, log_console.width, log_console.height)
        log_console.print_box(
            0, 0, log_console.width, 1, "┤Message history├", alignment=tcod.CENTER
        )

        self.engine.message_log.render_messages(
            log_console,
            1,
            1,
            log_console.width - 2,
            log_console.height - 2,
            self.engine.message_log.messages[: self.cursor + 1],
        )
        log_console.blit(console, 3, 3)

    def ev_keydown(self, event: tcod.event.KeyDown) -> Action | None:
        key = event.sym

        if key in CURSOR_Y_KEYS:
            adjust = CURSOR_Y_KEYS[key]
            if adjust < 0 and self.cursor == 0:
                self.cursor = self.log_length - 1
            elif adjust > 0 and self.cursor == self.log_length - 1:
                self.cursor = 0
            else:
                self.cursor = max(0, min(self.cursor + adjust, self.log_length - 1))
        elif key == tcod.event.K_HOME:
            self.cursor = 0
        elif key == tcod.event.K_END:
            self.cursor = self.log_length - 1
        else:
            self.engine.event_handler = MainGameEventHandler(self.engine)

        return None


class AskUserEventHandler(EventHandler):
    def handle_action(self, action: Action | None) -> bool:
        if super().handle_action(action):
            self.engine.event_handler = MainGameEventHandler(self.engine)
            return True
        return False

    def ev_keydown(self, event: tcod.event.KeyDown) -> Action | None:
        if event.sym in {
            tcod.event.K_LSHIFT,
            tcod.event.K_RSHIFT,
            tcod.event.K_LCTRL,
            tcod.event.K_RCTRL,
            tcod.event.K_LALT,
            tcod.event.K_RALT,
        }:
            return None
        return self.on_exit()

    def ev_mousebuttondown(self, event: tcod.event.MouseButtonDown) -> Action | None:
        return self.on_exit()

    def on_exit(self) -> Action | None:
        self.engine.event_handler = MainGameEventHandler(self.engine)
        return None


class InventoryEventHandler(AskUserEventHandler, ABC):
    title = "<missing title>"

    def on_render(self, console: tcod.Console) -> None:
        super().on_render(console)
        n_items_inventory = len(self.engine.player.inventory.items)
        height = max(n_items_inventory + 2, 3)

        x = 40 if self.engine.player.x <= 30 else 0
        y = 0
        width = len(self.title) + 4

        console.draw_frame(
            x=x,
            y=y,
            width=width,
            height=height,
            title=self.title,
            clear=True,
            fg=colour.WHITE,
            bg=colour.BLACK,
        )

        if n_items_inventory > 0:
            for i, item in enumerate(self.engine.player.inventory.items):
                item_key = chr(ord("a") + i)
                console.print(x + 1, y + i + 1, f"({item_key}) {item.name}")
        else:
            console.print(x + 1, y + 1, "(Empty)")

    def ev_keydown(self, event: tcod.event.KeyDown) -> Action | None:
        player = self.engine.player
        key = event.sym
        index = key - tcod.event.K_a

        if 0 <= index <= 26:
            try:
                selected = player.inventory.items[index]
            except IndexError:
                self.engine.log("Invalid entry.", colour.INVALID)
                return None
            return self.on_item_selected(selected)
        return super().ev_keydown(event)

    @abstractmethod
    def on_item_selected(self, item: Item) -> Action | None:
        ...


class InventoryActivateHandler(InventoryEventHandler):
    title = "Select an item to use"

    def on_item_selected(self, item: Item) -> Action | None:
        return item.consumable.get_action(self.engine.player)


class InventoryDropHandler(InventoryEventHandler):
    title = "Select an item to drop"

    def on_item_selected(self, item: Item) -> Action | None:
        return DropItem(self.engine.player, item)


class SelectIndexHandler(AskUserEventHandler, ABC):
    def __init__(self, engine: Engine):
        super().__init__(engine)
        player = self.engine.player
        engine.mouse_location = player.x, player.y

    def on_render(self, console: tcod.Console) -> None:
        super().on_render(console)
        x, y = self.engine.mouse_location
        console.tiles_rgb["bg"][x, y] = colour.WHITE
        console.tiles_rgb["fg"][x, y] = colour.WHITE

    def ev_keydown(self, event: tcod.event.KeyDown) -> Action | None:
        key = event.sym
        if key in MOVE_KEYS:
            modifier = 1
            if event.mod & (tcod.event.KMOD_LSHIFT | tcod.event.KMOD_RSHIFT):
                modifier *= 5
            if event.mod & (tcod.event.KMOD_LCTRL | tcod.event.KMOD_RCTRL):
                modifier *= 10
            if event.mod & (tcod.event.KMOD_LALT | tcod.event.KMOD_RALT):
                modifier *= 20

            x, y = self.engine.mouse_location
            dx, dy = MOVE_KEYS[key]
            x += dx * modifier
            y += dy * modifier
            x = max(0, min(x, self.engine.game_map.width - 1))
            y = max(0, min(y, self.engine.game_map.height - 1))
            self.engine.mouse_location = x, y
            return None
        elif key in CONFIRM_KEYS:
            return self.on_index_selected(*self.engine.mouse_location)
        return super().ev_keydown(event)

    def ev_mousebuttondown(self, event: tcod.event.MouseButtonDown) -> Action | None:
        if self.engine.game_map.in_bounds(*event.tile):
            if event.button == 1:
                return self.on_index_selected(*event.tile)
        return super().ev_mousebuttondown(event)

    @abstractmethod
    def on_index_selected(self, x: int, y: int) -> Action | None:
        ...


class LookHandler(SelectIndexHandler):
    def on_index_selected(self, x: int, y: int) -> None:
        self.engine.event_handler = MainGameEventHandler(self.engine)


ActionCallback = Callable[[tuple[int, int]], Optional[Action]]


class SingleRangedAttackHandler(SelectIndexHandler):
    def __init__(self, engine: Engine, callback: ActionCallback):
        super().__init__(engine)
        self.callback = callback

    def on_index_selected(self, x: int, y: int) -> Action | None:
        return self.callback((x, y))


class AreaRangedAttackHandler(SelectIndexHandler):
    def __init__(self, engine: Engine, radius: int, callback: ActionCallback):
        super().__init__(engine)
        self.radius = radius
        self.callback = callback

    def on_render(self, console: tcod.Console) -> None:
        super().on_render(console)

        x, y = self.engine.mouse_location
        console.draw_frame(
            x=x - self.radius - 1,
            y=y - self.radius - 1,
            width=self.radius ** 2,
            height=self.radius ** 2,
            fg=colour.RED,
            clear=False,
        )

    def on_index_selected(self, x: int, y: int) -> Action | None:
        return self.callback((x, y))
