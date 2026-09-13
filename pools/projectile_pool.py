
from general.entity import *
from data_and_definitions.projectile_definition import *
from utilities.projectile_utilities import *

class ProjectilePool: 

    def __init__(self, world: "World", size: int, basicdef: projectile_definition):
        self.world = world
        self.pool: list[Entity] = []

        for _ in range(size):
            e = spawn_projectile_from_def(
                basicdef, pygame.Vector2(0, 0)
            )
            e.active = False  
            self.pool.append(e)

    def _find_inactive(self) -> Entity | None:
        for e in self.pool:
            if not e.active:
                return e
        return None

    def _get(
            self,
            definition: projectile_definition,
            at: pygame.Vector2, 
            faction : Projectile_Targetting
            ) -> Entity:
        e = self._find_inactive()

        if e is None:
            e = spawn_projectile_from_def(definition, at)
            e.get(ProjectileComponent).define(faction, definition.lifetime, definition.pierces, definition.damage, definition.time_between_damage_instances, definition.crit_rate, definition.crit_damage_modifier, definition.sfx_on_collision)
            self.pool.append(e)
            return e

        get_reused_projectile(e, definition, at, faction)
        e.active = True
        return e

    def _return(self, e: Entity):
        reset_projectile(e)