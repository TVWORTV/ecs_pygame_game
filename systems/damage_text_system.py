
from components.on_screen_text import * 
from components.movement import * 

def damage_text_system(world, screen, camera, atlas, dt):
    for e in world.entities:
        dtext, movement = e.get(OnScreenTextComponent), e.get(MovementComponent)
        if not (dtext and movement):
            continue
        dtext.lifetime -= dt 
        if dtext.lifetime < 0:
            world.text_pool._return(e)
            world.remove_text(e)
            continue

        glyphs = atlas.crit if dtext.is_crit else atlas.normal

        if dtext.is_player:
            glyphs = atlas.player 
        elif dtext.is_crit:
            glyphs = atlas.crit 
        else: 
            glyphs = atlas.normal 

        screen_x, screen_y = camera.world_to_screen(movement.pos.x, movement.pos.y)
        for c in dtext.text:
            g = glyphs[c]
            screen.blit(g, (screen_x, screen_y))
            screen_x += g.get_width()