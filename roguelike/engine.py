from tcod.console import Console
from tcod.context import Context
from tcod.map import compute_fov

from roguelike.entity import Actor
from roguelike.game_map import GameMap
from roguelike.input_handlers import EventHandler


class Engine:
    game_map: GameMap

    def __init__(self, player: Actor) -> None:
        self.player = player
        self.event_handler = EventHandler(self)

    def render(self, console: Console, context: Context) -> None:
        self.game_map.render(console)
        context.present(console)
        console.clear()

    def update_fov(self) -> None:
        self.game_map.visible[:] = compute_fov(
            self.game_map.tiles["transparent"], (self.player.x, self.player.y), radius=8
        )
        self.game_map.explored |= self.game_map.visible

    def handle_enemy_turns(self) -> None:
        for entity in set(self.game_map.actors) - {self.player}:
            if entity.ai is not None:
                entity.ai.perform()
