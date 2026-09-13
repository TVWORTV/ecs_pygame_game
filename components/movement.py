import pygame


class MovementComponent:
    __slots__ = ("pos", "speed", "direction", "velocity", "can_move")

    def __init__(self, speed, x=0.0, y=0.0):
        self.pos = pygame.Vector2(x, y)
        self.direction = pygame.Vector2(0, 0)
        self.speed = speed
        self.velocity = pygame.Vector2(0, 0)
        self.can_move = True

    def is_moving(self, threshold: float = 0.1) -> bool:
        return self.velocity.length_squared() > threshold * threshold

    def reset(self):
        self.pos = pygame.Vector2(0, 0)
        self.direction = pygame.Vector2(0, 0)
        self.speed = 0.0
        self.velocity = pygame.Vector2(0, 0)
        self.can_move = True