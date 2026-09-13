import pygame
from dataclasses import dataclass
from general.entity import * 

@dataclass 
class DeathEvent: 
    entity_dead : Entity
    place_of_death : pygame.Vector2