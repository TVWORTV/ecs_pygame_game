import pygame
from collections import defaultdict

from components.collision import *
from components.movement import *
from components.enemy import *
from components.player import *
from components.projectile import *
from components.experience_point import *

from events.damage import *
from events.sfx_event import *

#region Grid 

CELL_SIZE = 16 

def _cell_coord(pos, cell_size):
    return (int(pos.x // cell_size), int(pos.y // cell_size))

def build_spatial_grid(entities, cell_size=CELL_SIZE):
    grid = defaultdict(list)
    for e in entities:
        pos, col = e.get(MovementComponent), e.get(Collider)
        if pos and col:
            grid[_cell_coord(pos.pos, cell_size)].append(e)
    return grid

def render_spatial_grid(screen, grid, cell_size, camera, font=None):
    screen_w, screen_h = screen.get_size()

    min_cx = int(camera.offset_x // cell_size)
    max_cx = int((camera.offset_x + screen_w / camera.zoom) // cell_size) + 1
    min_cy = int(camera.offset_y // cell_size)
    max_cy = int((camera.offset_y + screen_h / camera.zoom) // cell_size) + 1

    grid_color = (60, 60, 80)
    for cx in range(min_cx, max_cx + 1):
        x, _ = camera.world_to_screen(cx * cell_size, 0)
        pygame.draw.line(screen, grid_color, (x, 0), (x, screen_h))
    for cy in range(min_cy, max_cy + 1):
        _, y = camera.world_to_screen(0, cy * cell_size)
        pygame.draw.line(screen, grid_color, (0, y), (screen_w, y))

    if font is None:
        font = pygame.font.SysFont("consolas", 14)

    for (cx, cy), cell_entities in grid.items():
        count = len(cell_entities)
        if count == 0:
            continue

        cell_x, cell_y = camera.world_to_screen(cx * cell_size, cy * cell_size)
        color = (80, 220, 80) if count <= 2 else (230, 220, 60) if count <= 5 else (230, 60, 60)

        overlay = pygame.Surface((int(cell_size * camera.zoom), int(cell_size * camera.zoom)), pygame.SRCALPHA)
        overlay.fill((*color, 40))
        screen.blit(overlay, (cell_x, cell_y))

        txt = font.render(str(count), True, color)
        screen.blit(txt, (cell_x + 4, cell_y + 2))

#endregion 

def collision_system(grid, world, collect_effets):
    checked_pairs = set()
    for (cx, cy), cell_entities in grid.items():
        nearby = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nearby.extend(grid.get((cx + dx, cy + dy), []))

        for e1 in cell_entities:
            pos1, col1, en1, pl1, proj1, exp1 = (
                e1.get(MovementComponent), 
                e1.get(Collider),
                e1.get(EnemyComponent), 
                e1.get(PlayerComponent), 
                e1.get(ProjectileComponent),
                e1.get(ExperiencePointComponent)
                )
            for e2 in nearby:
                if e1 is e2:
                    continue
                pair_key = (id(e1), id(e2)) if id(e1) < id(e2) else (id(e2), id(e1))
                if pair_key in checked_pairs:
                    continue
                checked_pairs.add(pair_key)

                pos2, col2, en2, pl2, proj2, exp2 = (
                    e2.get(MovementComponent), 
                    e2.get(Collider),
                    e2.get(EnemyComponent), 
                    e2.get(PlayerComponent), 
                    e2.get(ProjectileComponent),
                    e2.get(ExperiencePointComponent)
                    )
                delta = pos2.pos - pos1.pos
                dist = delta.length()
                min_dist = col1.radius + col2.radius

                if dist < min_dist and (col1.can_collide == True and col2.can_collide == True):

#region Enemy and player 

                    if (en2 and pl1):
                        if pl1.damage_timer > 0.0:
                            continue 
                        pl1.damage_timer = pl1.time_between_damages

                        world.damage_events.append(DamageEvent(e1, en2.damage_on_hit, pos1.pos))

                    elif (en1 and pl2):  
                        if pl2.damage_timer > 0.0:
                            continue 
                        pl2.damage_timer = pl2.time_between_damages

                        world.damage_events.append(DamageEvent(e2, en1.damage_on_hit, pos2.pos))

#endregion 

#region Enemy and enemy

                    elif (en1 and en2): 
                        if dist == 0:
                            delta = pygame.Vector2(1, 0)
                            dist = 1
                        overlap = min_dist - dist
                        push = delta.normalize() * (overlap / 2)
                        pos1.pos -= push
                        pos2.pos += push

#endregion

#region Projectile + player

                    elif (pl1 and proj2):  
                        if proj2.faction_of_owner == Projectile_Targetting.PLAYER:
                            continue 
                        if not proj2.can_hit(e1, world.time):
                            continue
                        if pl1.damage_timer > 0.0:
                            continue 
                        pl1.damage_timer = pl1.time_between_damages

                        if proj2.register_hit(e1, world.time):
                            proj2.pierce_count += 1
                        if proj2.is_crit():
                            world.damage_events.append(DamageEvent(e1, proj2.damage + proj2.crit_damage, pos1.pos, True))
                        else:
                            world.damage_events.append(DamageEvent(e1, proj2.damage, pos1.pos, False))

                        world._sound_effect_events.append(
                            sfx_event(
                                proj2.sound_clip_collision,
                                pygame.Vector2(pos1.pos)
                            )
                        )

                    elif (proj1 and pl2): 
                        if proj1.faction_of_owner == Projectile_Targetting.PLAYER:
                            continue 
                        if not proj1.can_hit(e2, world.time):
                            continue
                        if pl2.damage_timer > 0.0:
                            continue 
                        pl2.damage_timer = pl2.time_between_damages

                        if proj1.register_hit(e2, world.time):
                            proj1.pierce_count += 1
                        if proj1.is_crit():
                            world.damage_events.append(DamageEvent(e2, proj1.damage + proj1.crit_damage, pos2.pos, True))
                        else:
                            world.damage_events.append(DamageEvent(e2, proj1.damage, pos2.pos, False))

                        world._sound_effect_events.append(
                            sfx_event(
                                proj1.sound_clip_collision,
                                pygame.Vector2(pos2.pos)
                            )
                        )
#endregion 

#region Projectile + enemy 

                    elif (en1 and proj2):  
                        if proj2.faction_of_owner == Projectile_Targetting.ENEMY:
                            continue 
                        if not proj2.can_hit(e1, world.time):
                            continue
                        if proj2.register_hit(e1, world.time):
                            proj2.pierce_count += 1
                        if proj2.is_crit():
                            world.damage_events.append(DamageEvent(e1, proj2.damage + proj2.crit_damage, pos1.pos, True))
                        else:
                            world.damage_events.append(DamageEvent(e1, proj2.damage, pos1.pos, False))

                        world._sound_effect_events.append(
                            sfx_event(
                                proj2.sound_clip_collision,
                                pygame.Vector2(pos1.pos)
                            )
                        )

                    elif (proj1 and en2): 
                        if proj1.faction_of_owner == Projectile_Targetting.ENEMY:
                            continue 
                        if not proj1.can_hit(e2, world.time):
                            continue
                        if proj1.register_hit(e2, world.time):
                            proj1.pierce_count += 1
                        if proj1.is_crit():
                            world.damage_events.append(DamageEvent(e2, proj1.damage + proj1.crit_damage, pos2.pos, True))
                        else:
                            world.damage_events.append(DamageEvent(e2, proj1.damage, pos2.pos, False))

                        world._sound_effect_events.append(
                            sfx_event(
                                proj1.sound_clip_collision,
                                pygame.Vector2(pos2.pos)
                            )
                        )

#endregion 

#region Exp + player

                    elif (exp1 and pl2):
                        sfx = collect_effets[random.randint(0, len(collect_effets)-1)]
                        world._sound_effect_events.append(sfx_event(sfx, pos1.pos))
                        world.experience_collected(e1, exp1.value)
                    elif (exp2 and pl1):
                        sfx = collect_effets[random.randint(0, len(collect_effets)-1)]
                        world._sound_effect_events.append(sfx_event(sfx, pos2.pos))
                        world.experience_collected(e2, exp2.value)

#endregion 
