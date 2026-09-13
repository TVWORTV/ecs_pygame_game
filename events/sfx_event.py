import pygame
from dataclasses import dataclass

@dataclass
class sfx_event:
    sfx : pygame.mixer.Sound
    at : pygame.Vector2