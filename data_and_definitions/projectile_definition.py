from dataclasses import dataclass
import pygame 

from components.animation import AnimationStateMachine


@dataclass
class projectile_definition:
    movement_speed: float
    damage: float
    pierces: int
    lifetime : float 
    animation_state_machine: AnimationStateMachine
    time_between_damage_instances: float = 0.2
    crit_rate : float = 0.1
    crit_damage_modifier : int = 1 # adds this to damage on crit 

    sfx_on_collision : pygame.mixer.Sound = None
    sfx_on_emission :  pygame.mixer.Sound = None