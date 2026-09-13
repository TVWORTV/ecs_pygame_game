import random
import copy
import pygame
from typing import TYPE_CHECKING

from general.entity import *
from components.movement import *
from components.health import *
from components.rendering import *
from components.animation import *
from components.enemy import *
from components.collision import * 
from components.special_rendering_tags import * 

from data_and_definitions.enemy_definition import *

from consts import *

if TYPE_CHECKING:
    from world.world import World


def spawn_enemy_from_def(
        enemydef: enemy_definition,
        at: pygame.Vector2,
        starting_clip: str,
        target: Entity,
        defaults: dict[str, float] = None
        ) -> Entity:
    sm = copy.deepcopy(enemydef.animation_state_machine)
    difficulty = defaults["difficulty"] if defaults is not None else 0

    e = Entity()
    e.active = True

    e.add(MovementComponent(enemydef.movement_speed + difficulty * DIFFICULTY_ENEMY_SPEED_CHANGE, at.x, at.y))
    e.add(HealthComponent(enemydef.health + difficulty * DIFFICULTY_ENEMY_HEALTH_CHANGE))
    e.add(RenderingComponent( layer=1))
    e.add(AnimationComponent(
        sm, starting_clip, random.randint(0, len(sm.states[starting_clip].frames) - 1)
    ))
    e.add(SpecialRenderingComponent(flips_with_dir=True, original_orientation=Rotation.RIGHT))
    e.add(EnemyComponent(target, enemydef.damage + difficulty * DIFFICULTY_ENEMY_DAMAGE_CHANGE))
    e.add(Collider(6 + difficulty * DIFFICULTY_ENEMY_SIZE_CHANGE))

    return e


def reset_enemy(e: Entity):
    health, movement, rendering, animation = (
        e.get(HealthComponent), e.get(MovementComponent),
        e.get(RenderingComponent), e.get(AnimationComponent)
    )
    e.active = False 
    if movement: movement.reset()
    if health: health.reset()
    if rendering: rendering.reset()
    if animation: animation.reset()

def get_reused_enemy(e, definition, at, starting_clip, world,
        defaults: dict[str, float] = None) -> Entity:
    movement = e.get(MovementComponent)
    animation = e.get(AnimationComponent)
    health = e.get(HealthComponent)
    enemy = e.get(EnemyComponent)
    collider = e.get(Collider)
    difficulty = defaults["difficulty"] if defaults is not None else 0

    enemy.damage_on_hit = definition.damage + difficulty * DIFFICULTY_ENEMY_DAMAGE_CHANGE
    enemy.target = world.player_entity

    collider.reset(6 + difficulty * DIFFICULTY_ENEMY_SIZE_CHANGE)

    movement.velocity = pygame.Vector2(0, 0)
    movement.direction = pygame.Vector2(0, 0)
    movement.speed = definition.movement_speed + difficulty * DIFFICULTY_ENEMY_SPEED_CHANGE
    movement.pos = pygame.Vector2(at)

    if animation.stateMachine.state_machine_name != definition.animation_state_machine.state_machine_name:
        animation.stateMachine = copy.deepcopy(definition.animation_state_machine)
        animation.stateMachine._rebuild_frame_event_lookup()

    animation.reset(starting_state=starting_clip)
    animation.frame_index = random.randint(
        0, len(animation.stateMachine.states[starting_clip].frames) - 1
    )

    health.max = health.current = definition.health + difficulty * DIFFICULTY_ENEMY_HEALTH_CHANGE
    health.respawn()
    e.active = True

    return e