from dataclasses import dataclass, field
from enum import Enum, auto

from data_and_definitions.projectile_definition import *
from components.animation import AnimationStateMachine

from components.health import * 
from components.enemy import * 
from components.movement import * 

@dataclass
class EnemyEffect:
    projectile: projectile_definition
    time_between_shots: float
    shooting_range: float


class ScalingType(Enum):
    HEALTH = auto()
    DAMAGE = auto()
    SPEED = auto()


@dataclass
class EnemyScaling:
    min_points_for_scale: int
    max_points_for_scale: int
    scale_type: ScalingType = ScalingType.HEALTH
    scaling_value: float = 0.1


@dataclass
class enemy_definition:
    movement_speed: float
    damage : float 
    health: int
    animation_state_machine: AnimationStateMachine
    enemy_scalings: list[EnemyScaling] = field(default_factory=list)
    additional_effects: list[EnemyEffect] = field(default_factory=list)


def _scaling_progress(points: int, min_points: int, max_points: int) -> float:
    if max_points <= min_points:
        return 1.0 if points >= min_points else 0.0
    if points <= min_points:
        return 0.0
    if points >= max_points:
        return 1.0
    return (points - min_points) / (max_points - min_points)
def apply_enemy_scaling(entity, definition: "enemy_definition", points: int) -> None:
    if not definition.enemy_scalings:
        return

    health_bonus = damage_bonus = speed_bonus = 0.0
    for scaling in definition.enemy_scalings:
        progress = _scaling_progress(points, scaling.min_points_for_scale, scaling.max_points_for_scale)
        if progress <= 0.0:
            continue
        bonus = scaling.scaling_value * min(1, progress) 
        if scaling.scale_type == ScalingType.HEALTH:
            health_bonus += bonus
        elif scaling.scale_type == ScalingType.DAMAGE:
            damage_bonus += bonus
        elif scaling.scale_type == ScalingType.SPEED:
            speed_bonus += bonus

    health = entity.get(HealthComponent)
    movement = entity.get(MovementComponent)
    enemy = entity.get(EnemyComponent)

    if health and health_bonus:
        health.max = max(1, round(definition.health + health_bonus)) 
        health.current = health.max
    if movement and speed_bonus:
        movement.speed = definition.movement_speed + speed_bonus      
    if enemy and damage_bonus:
        enemy.damage_on_hit = definition.damage + damage_bonus       