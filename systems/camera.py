from general.entity import *
from components.movement import * 
from world.world import *
from general.camera import *
from components.player import *

import pygame


def camera_follow_system(player_entity: Entity, camera: Camera, smooth_speed : float, dt :float):
    movement = player_entity.get(MovementComponent)
    if not movement:
        return
    
    target_x = movement.pos.x - camera.screen_width / 2 / camera.zoom
    camera.offset_x += (target_x - camera.offset_x) * min(1.0, smooth_speed * dt)

    target_y = movement.pos.y - camera.screen_height / 2 / camera.zoom
    camera.offset_y += (target_y - camera.offset_y) * min(1.0, smooth_speed * dt)