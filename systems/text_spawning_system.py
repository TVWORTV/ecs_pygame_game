from components.player import *
from components.movement import *
from components.on_screen_text import *

def text_spawning_system(world):
    for e in world.damage_events: 
        pl, movement = e.entity_damaged.get(PlayerComponent), e.entity_damaged.get(MovementComponent)
        if not movement:
            raise RuntimeError("damage event's entity has no movement???")

        player = False
        if pl: 
            player = True 

        text_entity = world.text_pool._get()

        text_entity_movement, text_entity_text = text_entity.get(MovementComponent), text_entity.get(OnScreenTextComponent)
        if not text_entity_movement:
            raise RuntimeError("text entity from pool has no movement component")
        if not text_entity_text:
            raise RuntimeError("text entity from pool has no text component")

        text_entity_movement.pos = pygame.Vector2(e.happened_at)
        text_entity_movement.direction = pygame.Vector2(0, -1)

        text_entity_text._set(f"{int(e.damage_amount)}", e.crit, player, world.text_lifetime)

        world.addEntity(text_entity)
        