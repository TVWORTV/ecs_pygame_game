from typing import TYPE_CHECKING

from components.movement import *

if TYPE_CHECKING:
    from world.world import World


def movement_system(world: "World", dt: float):
    for e in world.entities:
        movement = e.get(MovementComponent)
        if not movement or not movement.can_move:
            continue

        movement.velocity = movement.direction * movement.speed
        movement.pos += movement.velocity * dt