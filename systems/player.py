from general.entity import *
from components.movement import *
from world.world import *
from general.camera import *
from components.player import *

import pygame


def player_control_system(player_entity: Entity, events, move_up, move_down, move_left, move_right, dt : float):
    player = player_entity.get(PlayerComponent)
    if not player:
        raise RuntimeError("Wrong entity being passed to player control system")

    movement = player_entity.get(MovementComponent)
    if not movement:
        raise RuntimeError("player has no motion")

    dx = int(move_right.is_triggered(events)) - int(move_left.is_triggered(events))
    dy = int(move_down.is_triggered(events)) - int(move_up.is_triggered(events))

    direction = pygame.Vector2(dx, dy)
    if direction.length_squared() > 0:
        direction = direction.normalize()

    movement.direction = direction

    if player.damage_timer >=0:
        player.damage_timer -= dt