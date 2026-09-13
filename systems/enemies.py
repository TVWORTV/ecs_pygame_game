from typing import TYPE_CHECKING

from components.enemy import *
from components.movement import *

if TYPE_CHECKING:
    from world.world import World


def enemy_system(world: "World"):
    for e in world.entities:
        enemy, movement = e.get(EnemyComponent), e.get(MovementComponent)
        if not (enemy and movement):
            continue

        target = enemy.target.get(MovementComponent)
        if not target:
            continue

        direction = target.pos - movement.pos
        direction = direction.normalize()

        movement.direction = direction