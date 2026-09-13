import pygame

from data_and_definitions.enemy_definition import *
from general.entity import *

from components.experience_point import *
from components.movement import *
from components.collision import *
from components.rendering import *

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from world.world import World


class experience_pool:

    def __init__(self, world: "World", size: int, initial_value : int, image):
        self.world = world
        self.pool: list[Entity] = []
        self.image = image 

        for _ in range(size):
            e = Entity()
            e.add(ExperiencePointComponent(initial_value))
            e.add(Collider(12))
            e.add(RenderingComponent(self.image,  layer=-1))
            e.add(MovementComponent(0, 0, 0))

            e.active = False  
            self.pool.append(e)

    def _find_inactive(self) -> Entity | None:
        for e in self.pool:
            if not e.active:
                return e
        return None

    def _get(
            self,
            value,
            pos
            ) -> Entity:
        e = self._find_inactive()

        if e is None:
            e = Entity() 
            e.add(ExperiencePointComponent(value))
            e.add(MovementComponent(0, pos.x, pos.y))
            e.add(Collider(12))
            e.add(RenderingComponent(self.image,  layer=-1))
            self.pool.append(e)
            return e

        e.get(MovementComponent).pos = pygame.Vector2(pos.x, pos.y) 
        e.get(ExperiencePointComponent).set_params(value)

        e.active = True
        return e

    def _return(self, e: Entity):
        e.active = False
