
from typing import TYPE_CHECKING

from components.health import *

from events.death import *


if TYPE_CHECKING:
    from world.world import World


def death_system(world: "World"):
    for e in world.death_events:
        world.entity_death_aftermath(e.entity_dead, e.place_of_death)