from typing import TYPE_CHECKING

from components.health import *
from events.death import *

if TYPE_CHECKING:
    from world.world import World


def health_system(world: "World"):
    for e in world.damage_events:

        health = e.entity_damaged.get(HealthComponent)
        if not health:
            continue
        if health.invincibility_timer > 0.0:
            continue 

        health.current -= e.damage_amount
        health.current = int(health.current)
    
        if health.current <= 0 and not health.dying:  
            world.entity_death(e.entity_damaged, e.happened_at)
    