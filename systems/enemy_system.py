import random
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from world.world import World
    from pools.enemy_pool import *

from data_and_definitions.enemy_definition import *

def enemy_spawn_system(
        world: "World",
        pool: "EnemyPool",
        enemies_to_spawn: int,
        available_definitions: list[enemy_definition],
        starting_clip: str,
        defaults: dict[str, float] = None
        ):
    points = world.points

    for _ in range(enemies_to_spawn):
        def_to_use = available_definitions[random.randint(0, len(available_definitions) - 1)]
        entity = pool._get(def_to_use, world.get_enemy_spawn_pos(), starting_clip, defaults)
        apply_enemy_scaling(entity, def_to_use, points)
        world.addEntity(entity)