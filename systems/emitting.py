import pygame 

from world.world import *
from components.emitting import *
from components.projectile import *
from typing import TYPE_CHECKING

from components.movement import *
from components.player import *
from components.enemy import *

from events.projectile_spawn import *
from events.sfx_event import *

from general.entity import * 
from general.camera import *

if TYPE_CHECKING:
    from world.world import World

def emitting_system(world : "World", dt : float, joystick : bool):
    for e in world.entities:
        emitter = e.get(EmitterComponent)
        if not emitter: 
            continue 

        emitter.timer -= dt 
        if emitter.timer <= 0.0: 
            emitter.timer = emitter.time_between_shots

            enemy, player, movement = (
                emitter.owner.get(EnemyComponent),
                emitter.owner.get(PlayerComponent),
                emitter.owner.get(MovementComponent),
            )
            if not movement:
                raise RuntimeError("emitter has no movemnet")
            target_faction = Projectile_Targetting.PLAYER if player else Projectile_Targetting.ENEMY
            target = None 

            match(emitter.emission_type):
                case emitting_type.AT_TARGET: 
                    if enemy:
                        target = world.player_entity.get(MovementComponent).pos
                    elif player: 
                        if joystick: 
                            target = world.get_closest_enemy(movement.pos).get(MovementComponent).pos
                        else:
                            mouse_screen = pygame.mouse.get_pos()
                            mouse_world = Camera.get_instance().screen_to_world(*mouse_screen)  
                            target = pygame.Vector2(mouse_world)    
                case emitting_type.BEHIND: 
                        target = movement.direction * 2 
                case emitting_type.AHEAD: 
                        target = movement.direction * -2 
                case emitting_type.CLOSEST: 
                    if enemy:
                        target = world.player_entity.get(MovementComponent).pos
                    elif player: 
                        target = world.get_closest_enemy(movement.pos).get(MovementComponent).pos

            world.projectile_spawn_events.append(projectile_events(
                emitter.definition, 
                target_faction, 
                target, 
                pygame.Vector2(movement.pos)
                ))
            world._sound_effect_events.append(
                sfx_event(
                    emitter.definition.sfx_on_emission,
                    pygame.Vector2(movement.pos)
                )
            )