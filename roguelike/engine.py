from tcod.console import Console
from tcod.map import compute_fov

from roguelike.entity import Actor
from roguelike.game_map import GameMap
from roguelike.input_handlers import EventHandler, MainGameEventHandler
from roguelike.message_log import MessageLog
from roguelike.render_functions import render_bar, render_names_at_mouse_loc


class Engine:
    game_map: GameMap

    def __init__(self, player: Actor):
        self.player = player
        self.event_handler: EventHandler = MainGameEventHandler(self)
        self.message_log = MessageLog()
        self.mouse_location = (0, 0)

    def render(self, console: Console) -> None:
        self.game_map.render(console)
        self.message_log.render(console=console, x=21, y=45, width=40, height=5)

        render_bar(
            console=console,
            current_value=self.player.fighter.hp,
            max_value=self.player.fighter.max_hp,
            total_width=20,
        )
        render_names_at_mouse_loc(console=console, x=21, y=44, engine=self)

    def update_fov(self) -> None:
        self.game_map.visible[:] = compute_fov(
            self.game_map.tiles["transparent"], (self.player.x, self.player.y), radius=8
        )
        self.game_map.explored |= self.game_map.visible

    def handle_enemy_turns(self) -> None:
        for entity in set(self.game_map.actors) - {self.player}:
            if entity.ai is not None:
                entity.ai.perform()
