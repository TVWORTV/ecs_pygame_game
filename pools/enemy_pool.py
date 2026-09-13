from data_and_definitions.enemy_definition import *
from general.entity import *
from utilities.enemy_utilities import *

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from world.world import World



class EnemyPool: 

    def __init__(self, world: "World", size: int, basicdef: enemy_definition):
        self.world = world
        self.pool: list[Entity] = []

        for _ in range(size):
            e = spawn_enemy_from_def(
                basicdef, pygame.Vector2(0, 0), "idle", world.player_entity, None
            )
            e.active = False  
            self.pool.append(e)

    def _find_inactive(self) -> Entity | None:
        for e in self.pool:
            if not e.active:
                return e
        return None

    def _get(
            self,
            definition: enemy_definition,
            at: pygame.Vector2,
            starting_clip: str,
            defaults: dict[str, float] = None
            ) -> Entity:
        e = self._find_inactive()

        if e is None:
            e = spawn_enemy_from_def(definition, at, starting_clip, self.world.player_entity, defaults)
            self.pool.append(e)
            return e

        get_reused_enemy(e, definition, at, starting_clip, self.world, defaults)
        e.active = True
        return e

    def _return(self, e: Entity):
        reset_enemy(e)