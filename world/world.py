import random
import pygame
import random
import math
import sys

from general.inputAction import *
from consts import *
from world.world_progression import *
from data_and_definitions.enemy_definition import *
from systems.enemy_system import *
from pools.enemy_pool import *

from events.damage import *
from events.death import *

from systems.emitting import *
from abilities.ability_definition import *

from pools.projectile_pool import *
from pools.text_pool import *
from pools.exp_pool import *

from components.player import *
from components.emitting import *

class World:

    def __init__(self, 
                worldProgression: WorldProgression,
                player_entity: Entity,
                basic_definition_enemy : enemy_definition,
                basic_definition_proj : projectile_definition,
                text_lifetime : float, 
                exp_sprite,
                on_level_up, 
                on_player_death_callbacks,
                player_factory,
                ):
        self.entities: list[Entity] = []
        self.time = 0.0
        self.spawn_timer = 0.0
        self.enemy_spawn_timer = 0.0 

        self.points = 0
        self.points_highscore = 0

        self.emitters_by_id: dict[str, Entity] = {}

        self.progression = worldProgression
        self.player_entity = player_entity

        self.text_lifetime = text_lifetime

        self.enemies = []

        self.damage_events = []
        self.death_events = []
        self.projectile_spawn_events = []
        self._sound_effect_events = []

        self.enemy_pool = EnemyPool(self, 50, basic_definition_enemy)
        self.projectile_pool = ProjectilePool(self, 50, basic_definition_proj)
        self.text_pool = TextPool(self, 50, DAMAGE_TEXT_SPEED)
        self.exp_pool = experience_pool(self, 80, 5, exp_sprite)

        self.experience_threshold = EXPERIENCE_THRESHOLD_BASE
        self.experience_current = 0 

        self.on_level_up = on_level_up

        self.on_player_death_callbacks = on_player_death_callbacks
        self.player_factory = player_factory

    def update(self, dt: float, defaults: dict[str, float] = None):
        self.time += dt
        self.spawn_timer += dt
        self.enemy_spawn_timer += dt

        while self.spawn_timer >= 1.0:
            self.spawn_timer -= 1.0

            self.points += POINTS_PER_SECOND
            _, seconds = divmod(self.time, 60)

            self.progression.check_time(seconds)
            self.progression.check_points(self.points)

        spawn_interval = self.progression.spawn_interval()
        if spawn_interval > 0:
            while self.enemy_spawn_timer >= spawn_interval:
                self.enemy_spawn_timer -= spawn_interval
                enemy_spawn_system(
                    self,
                    self.enemy_pool,
                    1,
                    self.progression.enemies_available(),
                    "idle",
                    defaults
                )

#region events 

    def clear_frame_events(self):
        self.damage_events.clear()
        self.death_events.clear()
        self.projectile_spawn_events.clear()
        self._sound_effect_events.clear()

#endregion 
            

#region entities 

    def addEntity(self, e: Entity):
        self.entities.append(e)
        e.active = True
        enemy = e.get(EnemyComponent)
        if enemy: 
            self.enemies.append(e)

#region emitters

    def register_emitter(self, emitter_id: str, entity: Entity):
        self.emitters_by_id[emitter_id] = entity

    def get_emitter_entity(self, emitter_id: str) -> "Entity | None":
        return self.emitters_by_id.get(emitter_id)

    def remove_emitter(self, emitter_id: str):
        entity = self.emitters_by_id.pop(emitter_id, None)
        if entity is None:
            return
        if entity in self.entities:
            self.entities.remove(entity)
        entity.active = False

#endregion

    def get_closest_enemy(self, pos: pygame.Vector2) -> Entity:
        to_return = None
        closest_distance_sq = sys.float_info.max

        for e in self.enemies:
            e_mover, e_enemy = e.get(MovementComponent), e.get(EnemyComponent)
            if not (e_mover and e_enemy):
                continue

            distance_sq = pos.distance_squared_to(e_mover.pos)
            if distance_sq < closest_distance_sq:
                to_return = e
                closest_distance_sq = distance_sq

        return to_return

    def entity_death(self, e : Entity, place_of_death : pygame.Vector2):
        anim, collider, health, movement = e.get(AnimationComponent),e.get(Collider),e.get(HealthComponent), e.get(MovementComponent)
        if not health: 
            raise RuntimeError("entity called death with no health")
        if health.dying: 
            raise RuntimeError("dying entity called entity death")
        if not anim: 
            raise RuntimeError("dying entity has no anim")  
        health.dying = True
        collider.can_collide = False
        movement.can_move = False

    def entity_death_aftermath(self, e : Entity, place_of_death : pygame.Vector2):
        if e not in self.entities:
            return 
        self.entities.remove(e)
        e.active = False
        enemy, player = e.get(EnemyComponent), e.get(PlayerComponent)
        if enemy: 
            self.enemies.remove(e)
            self.enemy_pool._return(e)

            exp_entity = self.exp_pool._get(EXPERIENCE_AMOUNT_BASE, place_of_death)
            exp_entity.active = True
            self.addEntity(exp_entity)

            self.points += POINT_ON_DEATH
            
        if player: 
            self.reset_game()
            for callback in self.on_player_death_callbacks:
                callback()

    def remove_proj(self, e : Entity):
        self.entities.remove(e)
        e.active = False
        proj = e.get(ProjectileComponent) 
        if not proj:
            raise RuntimeError("tried removing proj but instead got a non projectile")
        self.projectile_pool._return(e)

    def remove_text(self, e : Entity):
        self.entities.remove(e)
        e.active = False 

    def _clear_entities(self):
        for entity in self.entities[:]:
            self.entities.remove(entity)
            if entity.get(EnemyComponent):
                self.enemy_pool._return(entity)
            elif entity.get(ProjectileComponent):
                self.projectile_pool._return(entity)
            elif entity.get(OnScreenTextComponent):
                self.text_pool._return(entity)
        self.enemies.clear()
        self.emitters_by_id.clear()

    def _respawn_player(self):
        new_player = self.player_factory()
        self.player_entity = new_player
        self.addEntity(new_player)
        self.ability_resolver.grant_starting_abilities()

#endregion 

    def reset_game(self):
        self._clear_entities()

        self.time = 0.0
        self.spawn_timer = 0.0
        self.enemy_spawn_timer = 0.0
        self.points_highscore = self.points
        self.points = 0
        
        self.experience_threshold = EXPERIENCE_THRESHOLD_BASE
        self.experience_current = 0

        self.progression.reset()
        self.clear_frame_events()
        self._respawn_player()

    def experience_collected(self, e : Entity, amount : int):
        self.entities.remove(e)
        e.active = False
        self.experience_current += amount
        self.try_level_up()

    def try_level_up(self):
        if self.experience_current >= self.experience_threshold:
            self.on_level_up()
            remainder = self.experience_current - self.experience_threshold
            self.experience_threshold = int(EXPERIENCE_INCREASE_MULTIPLIER * self.experience_threshold)
            self.experience_current = remainder

#region positions 

    def get_enemy_spawn_pos(self) -> pygame.Vector2:
        move = self.player_entity.get(MovementComponent)
        player_pos = move.pos

        return self.random_point_in_annulus(player_pos.x, player_pos.y, ENEMY_SPAWN_AREA.x, ENEMY_SPAWN_AREA.y)

    def random_point_in_annulus(self, cx, cy, r_inner, r_outer):
        angle = random.uniform(0, 2 * math.pi)
        r = math.sqrt(random.uniform(r_inner**2, r_outer**2))

        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle)
        return pygame.Vector2(x, y)

#endregion