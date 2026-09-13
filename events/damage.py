from dataclasses import dataclass, field
from general.entity import * 

import pygame

@dataclass 
class DamageEvent: 
    entity_damaged : Entity
    damage_amount : int 
    happened_at : pygame.Vector2
    crit : bool = False