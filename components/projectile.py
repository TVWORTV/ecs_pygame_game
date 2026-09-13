from enum import Enum, auto
import random

class Projectile_Targetting(Enum):
    ENEMY = auto()
    PLAYER = auto()

class ProjectileComponent:
    __slots__ = (
        "faction_of_owner", "lifetime", "lifetime_current",
        "pierce_count", "max_pierce", "time_between_damage_instances",
        "damage", "hit_entities", "crit_rate", "crit_damage", 
        "sound_clip_collision"
    )

    def __init__(self, faction_of_owner, lifetime, max_pierce, damage, time_between_damage_instances, crit_rate, crit_damage,sfx_on_col):
        self.define(faction_of_owner, lifetime, max_pierce, damage, time_between_damage_instances, crit_rate, crit_damage, sfx_on_col)

    def define(self, faction_of_owner, lifetime, max_pierce, damage, time_between_damage_instances, crit_rate, crit_damage, sfx_on_col):
        self.lifetime = lifetime
        self.lifetime_current = self.lifetime

        self.faction_of_owner = faction_of_owner
        self.max_pierce = max_pierce
        self.pierce_count = 0
        self.damage = damage

        self.time_between_damage_instances = time_between_damage_instances
        self.hit_entities = {}   

        self.crit_rate = crit_rate
        self.crit_damage = crit_damage

        self.sound_clip_collision = sfx_on_col

    def can_hit(self, entity, current_time: float) -> bool:
        next_allowed = self.hit_entities.get(id(entity))
        return next_allowed is None or current_time >= next_allowed

    def register_hit(self, entity, current_time: float) -> bool:
        eid = id(entity)
        is_first_hit = eid not in self.hit_entities

        if self.time_between_damage_instances > 0:
            self.hit_entities[eid] = current_time + self.time_between_damage_instances
        else:
            self.hit_entities[eid] = float("inf")   

        return is_first_hit

    def reset(self):
        self.define(Projectile_Targetting.ENEMY, 0.0, 0, 0, 0.0, 0, 0, None)

    def is_crit(self) -> bool:
        return random.random() < self.crit_rate
