
from pools.projectile_pool import *

def projectile_system(world, projectile_pool : ProjectilePool, dt : float ):
    for e in world.projectile_spawn_events:
        proj_entity = projectile_pool._get(e.projectile_def, e.shot_from, e.target_faction)
        movement = proj_entity.get(MovementComponent)
        if movement: 
            movement.direction = (e.shot_at - e.shot_from).normalize()

        world.addEntity(proj_entity)

    for p in world.entities: 
        proj = p.get(ProjectileComponent)
        if not proj: 
            continue 

        proj.lifetime_current -= dt 
        if proj.lifetime_current <= 0.0 or proj.pierce_count > proj.max_pierce: 
            world.remove_proj(p) 
