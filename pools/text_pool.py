import pygame

from data_and_definitions.enemy_definition import *
from general.entity import *

from components.on_screen_text import *
from components.movement import *

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from world.world import World



class TextPool: 

    def __init__(self, world: "World", size: int, speed):
        self.world = world
        self.pool: list[Entity] = []

        self.speed = speed 

        for _ in range(size):
            e = Entity()
            e.add(OnScreenTextComponent())
            e.add(MovementComponent(self.speed))

            e.active = False  
            self.pool.append(e)

    def _find_inactive(self) -> Entity | None:
        for e in self.pool:
            if not e.active:
                return e
        return None

    def _get(
            self,
            ) -> Entity:
        e = self._find_inactive()

        if e is None:
            e = Entity() 
            e.add(OnScreenTextComponent())
            e.add(MovementComponent(self.speed))
            self.pool.append(e)
            return e

        e.active = True
        return e

    def _return(self, e: Entity):
        e.active = False