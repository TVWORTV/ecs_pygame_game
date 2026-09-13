import random 
import copy
from typing import TYPE_CHECKING

from data_and_definitions.projectile_definition import *
from components.movement import *
from components.rendering import *
from components.animation import *
from components.collision import *
from components.projectile import *
from components.special_rendering_tags import *

from general.entity import *

from data_and_definitions.projectile_definition import *

if TYPE_CHECKING:
    from world.world import World


def spawn_projectile_from_def(
        projdef: projectile_definition,
        at: pygame.Vector2,
        ) -> Entity:
    sm = copy.deepcopy(projdef.animation_state_machine)

    e = Entity()
    e.active = True

    e.add(MovementComponent(projdef.movement_speed, at.x, at.y))
    e.add(RenderingComponent( layer=0))
    e.add(AnimationComponent(
        sm, "idle", random.randint(0, len(sm.states["idle"].frames) - 1)
    ))
    e.add(SpecialRenderingComponent(rotates_with_dir=True, original_rotation=Rotation.LEFT))
    e.add(Collider(7))
    e.add(ProjectileComponent(None, 0.1, 1, projdef.damage, projdef.time_between_damage_instances, projdef.crit_rate, projdef.crit_damage_modifier, projdef.sfx_on_collision))

    return e


def reset_projectile(e: Entity):
    movement, rendering, animation, proj = (
        e.get(MovementComponent),
        e.get(RenderingComponent), e.get(AnimationComponent), 
        e.get(ProjectileComponent)
    )
    e.active = False 
    if movement: movement.reset()
    if rendering: rendering.reset()
    if animation: animation.reset()
    if proj: proj.reset()


def get_reused_projectile(
        e: Entity,
        definition: projectile_definition,
        at: pygame.Vector2,
        faction : Projectile_Targetting
        ) -> Entity:
    movement = e.get(MovementComponent)
    animation = e.get(AnimationComponent)

    movement.velocity = pygame.Vector2(0, 0)
    movement.direction = pygame.Vector2(0, 0)
    movement.speed = definition.movement_speed
    movement.pos = pygame.Vector2(at)
    
    if animation.stateMachine.state_machine_name != definition.animation_state_machine.state_machine_name:
        animation.stateMachine = copy.deepcopy(definition.animation_state_machine)

    animation.stateMachine.current_state = "idle"
    animation.frame_index = random.randint(0, len(animation.stateMachine.states["idle"].frames) - 1)

    projectile = e.get(ProjectileComponent)
    projectile.define(faction, definition.lifetime, definition.pierces, definition.damage, definition.time_between_damage_instances, definition.crit_rate, definition.crit_damage_modifier, definition.sfx_on_collision)

    e.active = True 

    return e