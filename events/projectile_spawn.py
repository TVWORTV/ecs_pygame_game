import pygame
from dataclasses import dataclass
from components.player import *
from components.projectile import *
from data_and_definitions.projectile_definition import *

@dataclass
class projectile_events:
    projectile_def : projectile_definition 
    target_faction : Projectile_Targetting 
    shot_at : pygame.Vector2 # this is target 
    shot_from : pygame.Vector2 # this is the shooting point
