#region Imports

import pygame 
import asyncio
import random

from general.camera import *
from general.assets import *
from general.entity import *

from consts import *
from scenes.scene import *

from UI.bar import *
from UI.text import *
from UI.color import *
from UI.button import *
from UI.layoutGroup import *
from UI.slider import *

from abilities.ability_object import *
from abilities.player_ability import *

from world.world import *

from utilities.projectile_utilities import *
from utilities.text_utilities import *

from systems.health import *
from systems.movement import *
from systems.rendering import *
from systems.collision import *
from systems.player import *
from systems.enemies import *
from systems.animation_system import *
from systems.camera import *
from systems.emitting import *
from systems.projectile_system import *
from systems.death_system import *
from systems.text_spawning_system import *
from systems.damage_text_system import *
from systems.sound_effect_system import * 

from tiles.ruleTile import * 
from tiles.tilemap import *

from save_manager import * 

#endregion

#region Pygame default

pygame.mixer.pre_init(44100, -16, 2, 4096)
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(GAME_NAME)
clock = pygame.time.Clock()
FPS = 60

pygame.joystick.init()
joystick = pygame.joystick.Joystick(0) if pygame.joystick.get_count() > 0 else None

#endregion

#region SFXs

shot_1 = Assets.get_sound("files/sfxs/shot_1.ogg")
shot_2 = Assets.get_sound("files/sfxs/shot_2.ogg")
impact_1 = Assets.get_sound("files/sfxs/Impact.ogg")

collect_1 = Assets.get_sound("files/sfxs/collect_6.ogg")
collect_2 = Assets.get_sound("files/sfxs/collect_5.ogg")
collect_3 = Assets.get_sound("files/sfxs/collect_2.ogg")

collect_sounds = [collect_1, collect_2, collect_3]

death_1 = Assets.get_sound("files/sfxs/death_1.ogg")
death_2 = Assets.get_sound("files/sfxs/death_2.ogg")
death_3 = Assets.get_sound("files/sfxs/death_3.ogg")

death_sounds = [death_1, death_2, death_3]

#endregion

#region Fonts 

font_huge = Assets.get_font("files/fonts/ThaleahFat.ttf", 32)
font = Assets.get_font("files/fonts/ThaleahFat.ttf", 20)
tiny_font = Assets.get_font("files/fonts/ThaleahFat.ttf", 16)

atlas = DigitAtlas(font, "#DEB928", "#F89513", "#D71B1B")

#endregion 

#region Visuals 

#region UI 

hp_bar_bg = Assets.get_images_from_sheet("files/sprites/hp_bar.png", 16, 16)[0]  
hp_bar_fg = Assets.get_images_from_sheet("files/sprites/hp_bar.png", 16, 16)[1]  

buttons = Assets.get_images_from_sheet("files/sprites/buttons.png", 16, 16)
button_close = buttons[0]
button_pause = buttons[1]
button_next = buttons[2]
button_empty = buttons[3]

buttons_highlighted = Assets.get_images_from_sheet("files/sprites/buttons_highlighted.png", 16, 16)
buttons_highlighted_close = buttons_highlighted[0]
buttons_highlighted_pause = buttons_highlighted[1]
buttons_highlighted_next = buttons_highlighted[2]
buttons_highlighted_empty = buttons_highlighted[3]


ability_object_visuals = Assets.get_image("files/sprites/ability_object.png")
ability_object_visuals_hover =  Assets.get_image("files/sprites/ability_object_hover.png")

end_game_ui = Assets.get_image("files/sprites/end_game_ui.png")
end_game_ui_hover = Assets.get_image("files/sprites/end_game_ui_hover.png")


#endregion 

#region Projectile

projectile_frames_walk = Assets.get_images_from_sheet("files/sprites/projectiles.png", 32, 32)[0:3]
projectile_clip = AnimationClip(projectile_frames_walk, 0.14)

projectile_anim_sm  = AnimationStateMachine(
    states={
        "idle": projectile_clip
    },
    state_machine_name= "base"
)

sludge_toxic_frames_walk = Assets.get_image("files/sprites/toxic_sludge.png")
sludge_toxic_clip = AnimationClip([sludge_toxic_frames_walk], 0.14)

sludge_toxic_anim_sm  = AnimationStateMachine(
    states={
        "idle": sludge_toxic_clip
    },
    state_machine_name= "toxins"
)

light_purple_frames_walk = Assets.get_images_from_sheet("files/sprites/projectile_3.png", 32, 32)[0:4]
light_purple_clip = AnimationClip(light_purple_frames_walk, 0.14)

light_purple_anim_sm  = AnimationStateMachine(
    states={
        "idle": light_purple_clip
    },
    state_machine_name= "light_purple"
)

#endregion 

#region Enemies 

def add_death_event(world: "World", e: "Entity"):
    add_event(world, "death_events", DeathEvent(
        entity_dead=e,
        place_of_death=e.get(MovementComponent).pos
    ))
def add_sound_event(world: "World", e: "Entity"):
    add_event(world, "_sound_effect_events", sfx_event(
        death_sounds[random.randint(0, len(death_sounds)-1)],
        e.get(MovementComponent).pos
    ))

fly_frames_walk = Assets.get_images_from_sheet("files/sprites/fly.png", 16, 16)[0:5]  
fly_frames_death = Assets.get_images_from_sheet("files/sprites/fly_death.png", 16, 16)[0:4]  

fly_clip = AnimationClip(fly_frames_walk, 0.14)
fly_clip_death = AnimationClip(fly_frames_death, 0.14)

fly_anim_sm  = AnimationStateMachine(
    states={
        "idle": fly_clip,
        "death" : fly_clip_death,
    }, 
    state_machine_name= "fly",
    transitions=[
        Transition(
            from_state="idle",
            to_state="death",
            condition=is_dying,
            priority=0
        )
    ],
    frame_events=[
        FrameEvent("death", 3, [add_death_event]),
        FrameEvent("death", 1, [add_sound_event])
    ]
)

mosquito_frames_walk = Assets.get_images_from_sheet("files/sprites/mosquito.png", 32, 32)[0:5]  
mosquito_frames_death = Assets.get_images_from_sheet("files/sprites/mosquito_death.png", 32, 32)[0:5]  

mosquito_clip = AnimationClip(mosquito_frames_walk, 0.14)
mosquito_clip_death = AnimationClip(mosquito_frames_death, 0.14)

mosquito_anim_sm  = AnimationStateMachine(
    states={
        "idle": mosquito_clip,
        "death": mosquito_clip_death,
    }, 
    state_machine_name= "mosquito",
    transitions=[
        Transition(
            from_state="idle",
            to_state="death",
            condition=is_dying,
            priority=0
        )
    ],
    frame_events=[
        FrameEvent("death", 4, [add_death_event]),
        FrameEvent("death", 1, [add_sound_event])
    ]
)

hive_lord_frames_walk = Assets.get_images_from_sheet("files/sprites/hive_lord.png", 48, 48)[0:5]  
hive_lord_frames_death = Assets.get_images_from_sheet("files/sprites/hive_lord_death.png", 48, 48)[0:6]  

hive_lord_clip = AnimationClip(hive_lord_frames_walk, 0.14)
hive_lord_clip_death = AnimationClip(hive_lord_frames_death, 0.14)

hive_lord_anim_sm  = AnimationStateMachine(
    states={
        "idle": hive_lord_clip,
        "death": hive_lord_clip_death
    }, 
    state_machine_name= "hive_lord",
    transitions=[
        Transition(
            from_state="idle",
            to_state="death",
            condition=is_dying,
            priority=0
        )
    ],
    frame_events=[
        FrameEvent("death", 5, [add_death_event]),
        FrameEvent("death", 2, [add_sound_event])
    ]
)
#endregion 

#region Player 

player_frames_idle = Assets.get_images_from_sheet("files/sprites/character.png", 24, 20)[0:5]  
player_frames_walk = Assets.get_images_from_sheet("files/sprites/character.png", 24, 20)[6:12]  
player_frames_death = Assets.get_images_from_sheet("files/sprites/player_death.png", 24, 20)[0:6]  

player_clip_idle = AnimationClip(player_frames_idle, 0.14)
player_clip_walk = AnimationClip(player_frames_walk, 0.14)
player_clip_death = AnimationClip(player_frames_death, 0.14)

player_anim_sm = AnimationStateMachine(
    states={
        "idle": player_clip_idle,
        "walk": player_clip_walk,
        "death": player_clip_death,
    },
    transitions=[
        Transition("idle", "walk", is_moving),
        Transition("walk", "idle", is_idle),

        Transition("idle", "death", is_dying),
        Transition("walk", "death", is_dying),
    ],
    frame_events=[
        FrameEvent("death", 5, [add_death_event]),
    ]
)

#endregion 

#region Tiles 

tileset = Assets.get_images_from_sheet("files/sprites/tiles.png", 16, 16)
ground_tile = Tile(0)

#endregion 

#region Experience 

xp_point = Assets.get_image("files/sprites/XP_Point.png")
xp_bar_fill = Assets.get_image("files/sprites/exp_bar_fill.png")
xp_bar = Assets.get_image("files/sprites/exp_bar.png")

#endregion 

#endregion

#region Proj definition 

proj1 = projectile_definition(
    PROJECTILE_SPEED_DEFAULT, 
    PLAYER_DAMAGE_DEFAULT, 
    0, 
    6,
    projectile_anim_sm,
    time_between_damage_instances = 0.6,
    crit_damage_modifier= 1, 
    crit_rate= 0.1,
    sfx_on_collision= impact_1,
    )

toxic_sludge = projectile_definition(
    0, 
    1, 
    30, 
    10,
    sludge_toxic_anim_sm,
    time_between_damage_instances = 1,
    crit_damage_modifier= 1, 
    crit_rate= 0.05,
)

aimbot_proj = projectile_definition(
    PROJECTILE_SPEED_DEFAULT,
    5,
    0,
    6,
    projectile_anim_sm,
    crit_damage_modifier = 2,
    crit_rate = 0.10,
    sfx_on_collision= impact_1,
)

laser_proj = projectile_definition(
    PROJECTILE_SPEED_DEFAULT + 10,
    3,
    1,
    10,
    light_purple_anim_sm,
    time_between_damage_instances = 1,
    crit_damage_modifier = 2,
    crit_rate = 0.05,
    sfx_on_collision= impact_1,
)

#endregion

#region Player 

def create_player() -> Entity:
    player = Entity()
    player.add(PlayerComponent(TIME_BETWEEN_PLAYER_DAMAGES))
    player.add(MovementComponent(PLAYER_SPEED_DEFAULT))
    player.add(RenderingComponent(player_frames_idle[0], layer=1))
    player.add(SpecialRenderingComponent(flips_with_dir=True, original_orientation=Rotation.RIGHT))
    player.add(AnimationComponent(player_anim_sm, starting_clip="idle"))
    player.add(HealthComponent(PLAYER_HEALTH_DEFAULT))
    player.add(Collider(12))
    return player

#endregion 

#region Enemies 

enemy_fly = enemy_definition(
    ENEMY_SPEED_DEFAULT, 
    ENEMY_DAMAGE_DEFAULT,
    ENEMY_HEALTH_DEFAULT,
    fly_anim_sm,
    enemy_scalings=[
        EnemyScaling(
            min_points_for_scale=1200,
            max_points_for_scale=9000, 
            scale_type=ScalingType.HEALTH,
            scaling_value=100 
            ),
        EnemyScaling(
            min_points_for_scale=1200,
            max_points_for_scale=9000, 
            scale_type=ScalingType.SPEED,
            scaling_value=100 
            )
    ]
)

enemy_mosquito = enemy_definition(
    ENEMY_SPEED_DEFAULT * .85, 
    ENEMY_DAMAGE_DEFAULT,
    ENEMY_HEALTH_DEFAULT * 1.5,
    mosquito_anim_sm,
    enemy_scalings=[
        EnemyScaling(
            min_points_for_scale=1200,
            max_points_for_scale=9000, 
            scale_type=ScalingType.HEALTH,
            scaling_value=140 
            )
    ]
)

enemy_hive_lord = enemy_definition(
    ENEMY_SPEED_DEFAULT, 
    ENEMY_DAMAGE_DEFAULT * 1.2,
    ENEMY_HEALTH_DEFAULT * 2.2,
    hive_lord_anim_sm,
    enemy_scalings=[
        EnemyScaling(
            min_points_for_scale=1200,
            max_points_for_scale=9000, 
            scale_type=ScalingType.HEALTH,
            scaling_value=200 
            )
    ]
)

#endregion 

#region World 

def on_level_up():
    full_pause_game()
    sceneManager.current_scene.on_level_up_start(ability_resolver.get_random_abilities())

def pause_game(scene : "GameplayScene" = None):
    global PAUSED, FULLPAUSE
    if FULLPAUSE:
        return 
    PAUSED = not PAUSED
    sceneManager.current_scene.flip_settings()


def full_pause_game():
    global FULLPAUSE, PAUSED 
    FULLPAUSE = not FULLPAUSE 
    PAUSED = not PAUSED
    
def on_loss():
    full_pause_game() 
    sceneManager.current_scene.open_end_game_ui()
    

wprogress = WorldProgression(
    time_brackets=[
        TimeProgressionBracket(0, 1.8),
        TimeProgressionBracket(20, 1.3), 
        TimeProgressionBracket(40, 1), 
        TimeProgressionBracket(65, 0.05), 
        TimeProgressionBracket(80, 0.001), 
        TimeProgressionBracket(110, 0.0001), 
        TimeProgressionBracket(125, 0.00001), 
        TimeProgressionBracket(150, 0.000001), 
        TimeProgressionBracket(180, 0.0000001), 
    ],
    point_brackets= [
        PointProgressionBracket(
            0, 
            enemies_available= [
                enemy_fly
            ]
            ),
        PointProgressionBracket(
            100, 
            enemies_available=[
                enemy_fly,
                enemy_mosquito,
            ]
        ),
        PointProgressionBracket(
            300, 
            enemies_available=[
                enemy_mosquito,
                enemy_hive_lord 
            ]
        ),
        PointProgressionBracket(
            600, 
            enemies_available=[
                enemy_fly,
                enemy_mosquito,
                enemy_hive_lord 
            ]
        ),
    ]
)
def reset_resolver():
    ability_resolver.restart()

player = create_player()
world = World(wprogress, player, enemy_fly, proj1, DAMAGE_TEXT_LIFETIME, xp_point, on_level_up, [on_loss, reset_resolver], create_player)
world.addEntity(player)

#endregion

#region Saving 

save_manager = saveManager()

#endregion 

#region Abilities

default_weapon = PlayerAbility(
    _name="Default Weapon",
    _description="Your basic attack.",
    dependant_on=[],
    effects=[
        AddEmitter(
            emitter_id="default",
            definition=proj1,
            type=emitting_type.AT_TARGET,
            time_between_shots=0.4,
        ),
    ],
)

#region Toxins

toxins_1 = PlayerAbility(
    _name="Toxins",
    _description="You leave behind \npools of acid that \ndamage enemies.",
    dependant_on=[],
    effects=[
        AddEmitter(
            emitter_id="toxic_sludge",
            definition=toxic_sludge,
            type=emitting_type.BEHIND,
            time_between_shots=0.8,
        ),
    ],
)

toxins_2 = PlayerAbility(
    _name="Toxins 2",
    _description="You leave acid \n more often",
    dependant_on=[toxins_1],
    effects=[
        ModifyEmitter(
            target_emitter_id="toxic_sludge",
            modifiers=[
                StatModifier(TIME_BETWEEN_SHOTS, ModifierOp.ADD, -0.2),
            ],
        ),
    ],
)

toxins_3 = PlayerAbility(
    _name="Toxins 3",
    _description="Acid pools deal \nmore damage.",
    dependant_on=[toxins_2],
    effects=[
        ModifyEmitter(
            target_emitter_id="toxic_sludge",
            modifiers=[
                StatModifier("damage", ModifierOp.ADD, 1),
                StatModifier("crit_damage_modifier", ModifierOp.ADD, 1),
            ],
        ),
    ],
)

toxins_4 = PlayerAbility(
    _name="Toxins 4",
    _description="Increases crit \nrate and crit \ndamage.",
    dependant_on=[toxins_3],
    effects=[
        ModifyEmitter(
            target_emitter_id="toxic_sludge",
            modifiers=[
                StatModifier("crit_rate", ModifierOp.ADD, 0.05),
                StatModifier("crit_damage_modifier", ModifierOp.ADD, 1),
            ],
        ),
    ],
)

toxins_5 = PlayerAbility(
    _name="Toxins 5",
    _description="You leave behind \nmore acid.\nIncreases movement \nspeed",
    dependant_on=[toxins_4],
    effects=[
        ModifyEmitter(
            target_emitter_id="toxic_sludge",
            modifiers=[
                StatModifier(TIME_BETWEEN_SHOTS, ModifierOp.ADD, -0.2),
            ],
        ),
        StatChange(
            speed_change=15.0
        )
    ],
)


#endregion 

#region Aim bot

aimbot_1 = PlayerAbility(
    _name="Aim bot",
    _description="Additional shooting \nmodule that shoots at \nthe closest enemy.",
    dependant_on=[],
    effects=[
        AddEmitter(
            emitter_id="aimbot_1",
            definition=aimbot_proj,
            type=emitting_type.CLOSEST,
            time_between_shots=1.2,
        ),
    ],
)

aimbot_2 = PlayerAbility(
    _name="Aim bot 2",
    _description="+2 more aim bot \nmodules (same stats).",
    dependant_on=[aimbot_1],
    effects=[
        AddEmitter(
            emitter_id="aimbot_2",
            definition=aimbot_proj,
            type=emitting_type.CLOSEST,
            time_between_shots=1.2,
        ),
    ],
)

aimbot_3 = PlayerAbility(
    _name="Aim bot 3",
    _description="Adds one aim bot.\nAll bots shoot faster.",
    dependant_on=[aimbot_2],
    effects=[
        AddEmitter(
            emitter_id="aimbot_3",
            definition=aimbot_proj,
            type=emitting_type.CLOSEST,
            time_between_shots=1.2,
        ),
        ModifyEmitter(target_emitter_id="aimbot_1", modifiers=[
            StatModifier(TIME_BETWEEN_SHOTS, ModifierOp.ADD, -0.3),
        ]),
        ModifyEmitter(target_emitter_id="aimbot_2", modifiers=[
            StatModifier(TIME_BETWEEN_SHOTS, ModifierOp.ADD, -0.3),
        ]),
        ModifyEmitter(target_emitter_id="aimbot_3", modifiers=[
            StatModifier(TIME_BETWEEN_SHOTS, ModifierOp.ADD, -0.3),
        ]),
    ],
)

aimbot_4 = PlayerAbility(
    _name="Aim bot 4",
    _description="All aim bots get \nhigher crit rate and \nfire even faster.",
    dependant_on=[aimbot_3],
    effects=[
        ModifyEmitter(target_emitter_id="aimbot_1", modifiers=[
            StatModifier("crit_rate", ModifierOp.ADD, 0.10),
            StatModifier(TIME_BETWEEN_SHOTS, ModifierOp.ADD, -0.1),
        ]),
        ModifyEmitter(target_emitter_id="aimbot_2", modifiers=[
            StatModifier("crit_rate", ModifierOp.ADD, 0.10),
            StatModifier(TIME_BETWEEN_SHOTS, ModifierOp.ADD, -0.1),
        ]),
        ModifyEmitter(target_emitter_id="aimbot_3", modifiers=[
            StatModifier("crit_rate", ModifierOp.ADD, 0.10),
            StatModifier(TIME_BETWEEN_SHOTS, ModifierOp.ADD, -0.1),
        ]),
    ],
)

#endregion

#region Laser

laser_1 = PlayerAbility(
    _name="Laser",
    _description="Additional projectile \nthat shoots pierces \nenemies.",
    dependant_on=[],
    effects=[
        AddEmitter(
            emitter_id="laser",
            definition=laser_proj,
            type=emitting_type.AT_TARGET,
            time_between_shots=1.0,
        ),
    ],
)

laser_2 = PlayerAbility(
    _name="Laser 2",
    _description="Laser pierces\n3 additional enemies.",
    dependant_on=[laser_1],
    effects=[
        ModifyEmitter(
            target_emitter_id="laser",
            modifiers=[
                StatModifier("pierces", ModifierOp.ADD, 4),
            ],
        ),
    ],
)

laser_3 = PlayerAbility(
    _name="Laser 3",
    _description="Laser deals\n higher damage.",
    dependant_on=[laser_2],
    effects=[
        ModifyEmitter(
            target_emitter_id="laser",
            modifiers=[
                StatModifier("damage", ModifierOp.ADD, 5),
            ],
        ),
    ],
)

laser_4 = PlayerAbility(
    _name="Laser 4",
    _description="+1 pierce, \n+5% crit rate, \ncrit damage changes to +3.",
    dependant_on=[laser_3],
    effects=[
        ModifyEmitter(
            target_emitter_id="laser",
            modifiers=[
                StatModifier("pierces", ModifierOp.ADD, 1),
                StatModifier("crit_rate", ModifierOp.ADD, 0.05),
                StatModifier("crit_damage_modifier", ModifierOp.ADD, 1),
            ],
        ),
    ],
)

#endregion 

#region Hermes 

hermes_1 = PlayerAbility(
    _name="Hermes Boots",
    _description="Increase your \nmovement speed.",
    dependant_on=[],
    effects=[
        StatChange(
            speed_change=15.0
        )
    ],
)

hermes_2 = PlayerAbility(
    _name="Hermes Boots 2",
    _description="Increase your default\nweapon's speed.",
    dependant_on=[hermes_1],
    effects=[
        ModifyEmitter(
            target_emitter_id="default",
            modifiers=[
                StatModifier(TIME_BETWEEN_SHOTS, ModifierOp.ADD, -0.1),
            ],
        ),
    ],
)

hermes_3 = PlayerAbility(
    _name="Hermes Boots 3",
    _description="Greatly ncrease\n your default\nweapon's speed.",
    dependant_on=[hermes_2],
    effects=[
        ModifyEmitter(
            target_emitter_id="default",
            modifiers=[
                StatModifier(TIME_BETWEEN_SHOTS, ModifierOp.ADD, -0.15),
            ],
        ),
    ],
)

hermes_4 = PlayerAbility(
    _name="Hermes Boots 4",
    _description="Increase your \nshooting speed.",
    dependant_on=[hermes_3, toxins_1, laser_1, aimbot_3],
    effects=[
        ModifyEmitter(target_emitter_id="aimbot_1", modifiers=[
            StatModifier(TIME_BETWEEN_SHOTS, ModifierOp.ADD, -0.1),
        ]),
        ModifyEmitter(target_emitter_id="aimbot_2", modifiers=[
            StatModifier(TIME_BETWEEN_SHOTS, ModifierOp.ADD, -0.1),
        ]),
        ModifyEmitter(target_emitter_id="aimbot_3", modifiers=[
            StatModifier(TIME_BETWEEN_SHOTS, ModifierOp.ADD, -0.1),
        ]),
        ModifyEmitter(target_emitter_id="default", modifiers=[
            StatModifier(TIME_BETWEEN_SHOTS, ModifierOp.ADD, -0.1),
        ]),
        ModifyEmitter(target_emitter_id="laser", modifiers=[
            StatModifier(TIME_BETWEEN_SHOTS, ModifierOp.ADD, -0.1),
        ]),
        ModifyEmitter(target_emitter_id="toxic_sludge", modifiers=[
            StatModifier(TIME_BETWEEN_SHOTS, ModifierOp.ADD, -0.1),
        ]),
    ],
)

#endregion 

#region Gear 

gear_1 = PlayerAbility(
    _name="Gear",
    _description="Increase your HP.",
    dependant_on=[],
    effects=[
        StatChange(
            health_change=15.0
        )
    ],
)

gear_2 = PlayerAbility(
    _name="Gear 2",
    _description="Increase your default\nweapon's damage.",
    dependant_on=[gear_1],
    effects=[
        ModifyEmitter(
            target_emitter_id="default",
            modifiers=[
                StatModifier("damage", ModifierOp.ADD, 2),
            ],
        ),
    ],
)

gear_3 = PlayerAbility(
    _name="Gear 3",
    _description="Increase your default\nweapon's crit rate \n and crit damage.",
    dependant_on=[gear_2],
    effects=[
        ModifyEmitter(
            target_emitter_id="default",
            modifiers=[
                StatModifier("crit_rate", ModifierOp.ADD, 0.1),
                StatModifier("crit_damage_modifier", ModifierOp.ADD, 2),
            ],
        ),
    ],
)

gear_4 = PlayerAbility(
    _name="Gear",
    _description="Increase your HP.",
    dependant_on=[gear_3],
    effects=[
        StatChange(
            health_change=15.0
        )
    ],
)

gear_5 = PlayerAbility(
    _name="Gear 3",
    _description="Greatly empower \n your default \n weapon",
    dependant_on=[gear_4],
    effects=[
        ModifyEmitter(
            target_emitter_id="default",
            modifiers=[
                StatModifier("crit_rate", ModifierOp.ADD, 0.1),
                StatModifier("crit_damage_modifier", ModifierOp.ADD, 1),
                StatModifier("damage", ModifierOp.ADD, 1),
            ],
        ),
    ],
)


#endregion 

#region Reusable 

reusable_1 = PlayerAbility(
    _name="Power Up",
    _description="Increase your HP by 20.",
    dependant_on=[],
    effects=[
        StatChange(
            health_change = 20
        )
    ],
)

reusable_2 = PlayerAbility(
    _name="Speed Buff",
    _description="Increase your movement speed.",
    dependant_on=[],
    effects=[
        StatChange(
            speed_change=10.0
        )
    ],
)

reusable_3 = PlayerAbility(
    _name="",
    _description="Increase your HP and speed \nby a little bit.",
    dependant_on=[],
    effects=[
        StatChange(
            health_change = 5,
            speed_change=2.0
        )
    ],
)

#endregion 

#region Combo 

combo_laser_toxic = PlayerAbility(
    _name="Combo: Toxic+Laser",
    _description="Greatly empowers \nboth abilities",
    dependant_on=[toxins_5, laser_4],
    effects=[
        ModifyEmitter(
            target_emitter_id="toxic_sludge",
            modifiers=[
                StatModifier("time_between_damage_instances", ModifierOp.ADD, -0.1),
                StatModifier("crit_rate", ModifierOp.ADD, 0.1),
            ],
        ),
        ModifyEmitter(
            target_emitter_id="laser",
            modifiers=[
                StatModifier("pierces", ModifierOp.ADD, 5),
                StatModifier("crit_rate", ModifierOp.ADD, 0.1),
                StatModifier("crit_damage_modifier", ModifierOp.ADD, 1),
            ],
        ),
    ],
)

combo_toxins_aimbot = PlayerAbility(
    _name="Combo: Toxic+Aimbot",
    _description="Greatly empowers \nboth abilities",
    dependant_on=[toxins_5, aimbot_4],
    effects=[
        ModifyEmitter(
            target_emitter_id="toxic_sludge",
            modifiers=[
                StatModifier(TIME_BETWEEN_SHOTS, ModifierOp.ADD, -0.2),
                StatModifier("crit_rate", ModifierOp.ADD, 0.1),
            ],
        ),
        ModifyEmitter(
            target_emitter_id="aimbot_1",
            modifiers=[
                StatModifier("damage", ModifierOp.ADD, 3),
            ],
        ),
        ModifyEmitter(
            target_emitter_id="aimbot_2",
            modifiers=[
                StatModifier("damage", ModifierOp.ADD, 3),
            ],
        ),
        ModifyEmitter(
            target_emitter_id="aimbot_3",
            modifiers=[
                StatModifier("damage", ModifierOp.ADD, 3),
            ],
        ),
    ],
)

combo_laser_aimbot = PlayerAbility(
    _name="Combo: Laser+Aimbot",
    _description="Greatly empowers \nboth abilities",
    dependant_on=[laser_4, aimbot_4],
    effects=[
        ModifyEmitter(
            target_emitter_id="laser",
            modifiers=[
                StatModifier(TIME_BETWEEN_SHOTS, ModifierOp.ADD, -0.2),
                StatModifier("crit_rate", ModifierOp.ADD, 0.1),
                StatModifier("crit_damage_modifier", ModifierOp.ADD, 3),
            ],
        ),
        ModifyEmitter(
            target_emitter_id="aimbot_1",
            modifiers=[
                StatModifier("pierces", ModifierOp.ADD, 3),
            ],
        ),
        ModifyEmitter(
            target_emitter_id="aimbot_2",
            modifiers=[
                StatModifier("pierces", ModifierOp.ADD, 3),
            ],
        ),
        ModifyEmitter(
            target_emitter_id="aimbot_3",
            modifiers=[
                StatModifier("pierces", ModifierOp.ADD, 3),
            ],
        ),
    ],
)
#endregion 

ability_library = AbilityLibrary(
    all_abilities=[
        toxins_1, toxins_2, toxins_3, toxins_4, toxins_5,
        aimbot_1, aimbot_2, aimbot_3, aimbot_4,
        laser_1, laser_2, laser_3, laser_4,
        hermes_1, hermes_2, hermes_3, hermes_4,
        gear_1, gear_2, gear_3, gear_4, gear_5,
        combo_laser_toxic, combo_toxins_aimbot, combo_laser_aimbot
    ],
    repeatable_abilities=[
        reusable_1,
        reusable_2,
        reusable_3
    ],
    starting_abilities=[
        default_weapon,
    ],
)

ability_resolver = AbilityResolver(ability_library, world)
world.ability_resolver = ability_resolver
ability_resolver.grant_starting_abilities()

#endregion

#region Music 

bgm = Assets.get_bgm("files/bgm.ogg")

def playBgm(loop=True, fade_ms=0):
    if not bgm:
        return
    pygame.mixer.music.load(bgm)
    pygame.mixer.music.set_volume(save_manager.musicSettings)
    pygame.mixer.music.play(-1 if loop else 0, fade_ms=fade_ms)

def setMusicVolume(value : float):
    pygame.mixer.music.set_volume(value)

def stopBgm(fade_ms=0):
    if fade_ms:
        pygame.mixer.music.fadeout(fade_ms)
    else:
        pygame.mixer.music.stop()

#endregion 

#region Scenes 

class GameplayScene(Scene):
    def __init__(self, manager):
        super().__init__(manager)

        #region Settings 

        panel_size = (WIDTH / 2, HEIGHT - HEIGHT / 4)
        panel_pos = (WIDTH / 2 - panel_size[0]/2, HEIGHT / 2 - 192)

        self.settings_panel = StaticImage(
            end_game_ui, panel_pos, size=panel_size, nineSliced=True, border=3
        )

        slider_x = 32
        slider_width = panel_size[0] - 64
        slider_height = 24

        self.music_label = StaticText("Music", font, (slider_x, 32), color=Color("#000000"))
        self.music_slider = UISlider(
            slider_x, 64, slider_width, slider_height,
            end_game_ui, 3,
            handleImage=end_game_ui_hover, handleWidth=16,
            currentValue=save_manager.musicSettings, maxValue=1.0,
            onChange=self.on_music_changed
        )

        self.sfx_label = StaticText("SFX", font, (slider_x, 112), color=Color("#000000"))
        self.sfx_slider = UISlider(
            slider_x, 144, slider_width, slider_height,
            end_game_ui, 3,
            handleImage=end_game_ui_hover, handleWidth=16,
            currentValue=save_manager.sfxSettings, maxValue=1.0,
            onChange=self.on_sfx_changed
        )

        self.difficulty_label = StaticText("Difficulty", font, (slider_x, 192), color=Color("#000000"))
        self.difficulty_slider = UISlider(
            slider_x, 224, slider_width, slider_height,
            end_game_ui, 3,
            handleImage=end_game_ui_hover, handleWidth=16,
            currentValue=save_manager.difficulty, maxValue=5.0,
            onChange=self.on_difficulty_changed
        )
        self.exit_button = Button(
            (panel_size[0]/2+75, panel_size[1] - 80, 150,35), 
            font, 
            self.on_main_menu_clicked, 
            "Main Menu", 
            end_game_ui, 
            end_game_ui_hover,
            True,
            3, 
            Color("#EACA16")
            )
        self.resume_button = Button(
            (panel_size[0]/2-225, panel_size[1] - 80, 150,35), 
            font, 
            pause_game, 
            "Resume", 
            end_game_ui, 
            end_game_ui_hover,
            True,
            3, 
            Color("#EACA16")
            )

        for settings_obj in (
            self.music_label, self.music_slider,
            self.sfx_label, self.sfx_slider,
            self.difficulty_label, self.difficulty_slider,
            self.exit_button, self.resume_button
        ):
            self.settings_panel.addChild(settings_obj)


        #endregion 

        #region General UI 

        self.hp_bar = UIBar(15,15,250, 40, hp_bar_fg, 1, hp_bar_bg, True, 1)
        self.addobj(self.hp_bar)

        self.text_bar = StaticText("0 / 0", font, (0,0), Color("#000000"), drawOrder= 1)
        self.hp_bar.addChild(self.text_bar)

        self.text_bar.setPos(
            (
                self.hp_bar.getSize()[0]/2 - self.text_bar.getSize()[0], 
                self.hp_bar.getSize()[1]/2 - self.text_bar.getSize()[1]/3
            )
            )
        self.addobj(self.text_bar)

        self.pasue_button = Button(
            (15, 65, 32, 32),
            None, 
            pause_game,
            image=button_pause,
            hoverImage=buttons_highlighted_pause
        )
        self.addobj(self.pasue_button) 

        #endregion 

        #region Experience

        self.xp_bar = UIBar(WIDTH/2-256, HEIGHT*0.9,512, 32, xp_bar_fill, 1/7, xp_bar)
        self.xp_bar_text = StaticText("0 / 0", font, (0,0), Color("#000000"), drawOrder= 1)
        self.addobj(self.xp_bar)
        self.xp_bar.addChild(self.xp_bar_text)

        self.xp_bar_text.setPos(
            (
                self.xp_bar.getSize()[0]/2 - self.xp_bar_text.getSize()[0], 
                self.xp_bar.getSize()[1]/2 - self.xp_bar_text.getSize()[1]/2
            )
            )
        self.addobj(self.xp_bar_text)

        #endregion

        #region Abilities 

        i = 0 
        ability_layout_group = LayoutGroup(LayoutType.horizontal, 96 * UI_SCALE, (96, 100))
        self.ability_objects = []

        while i < 3:
            i+=1
            new_ability_object = AbilityObject(
                pygame.Vector2(HEIGHT/3-(32*UI_SCALE),HEIGHT/6), 
                pygame.Vector2(64 * UI_SCALE, 96 * UI_SCALE), 
                ability_object_visuals, 
                ability_object_visuals_hover,
                callbacks_on_selection=[
                    full_pause_game, 
                    self.on_level_up_end
                ],
                ability_resolver=ability_resolver, 
                name_font = font,
                desc_font = tiny_font,
                name_text_pos= pygame.Vector2(16*UI_SCALE, 48*UI_SCALE),
                desc_text_pos= pygame.Vector2(8*UI_SCALE, 56*UI_SCALE)
                )
            self.ability_objects.append(new_ability_object)
            ability_layout_group.addToGroup(new_ability_object)

        self.ability_layout_group = ability_layout_group

        #endregion 
        
        #region End game INIT

        end_game_panel_size = pygame.Vector2(256, 144)
        end_game_panel_pos = pygame.Vector2(
            (WIDTH / 2) - end_game_panel_size.x / 2,
            (HEIGHT / 2) - end_game_panel_size.y / 2
        )

        self.end_game_panel = StaticImage(
            end_game_ui,
            end_game_panel_pos,
            size=end_game_panel_size,
            nineSliced=True,
            border=3,
            drawOrder=2
        )

        self.end_game_text = StaticText("-", 
                                        font, 
                                        (55, 25),
                                        Color("#FF8630"),
                                        )
        
        self.end_game_panel.addChild(self.end_game_text)

        end_game_buttons = LayoutGroup(
            LayoutType.horizontal,
            16,
            (24, self.end_game_panel.getSize()[0]/4)
        )
        self.end_game_panel.addChild(end_game_buttons)

        self.restart_button = Button(
            (0, 0, 96, 32),
            font,
            self.on_restart_clicked,
            "Restart!",
            end_game_ui,
            end_game_ui_hover,
            True,
            3,
        )

        self.main_menu_button = Button(
            (0, 0, 96, 32),
            font,
            self.on_main_menu_clicked,
            "Main Menu!",
            end_game_ui,
            end_game_ui_hover,
            True,
            3,
        )

        end_game_buttons.addToGroup(self.restart_button)
        end_game_buttons.addToGroup(self.main_menu_button)

        self.end_game_buttons = end_game_buttons
        self._end_game_open = False

        #endregion

    #region End game Ui 

    def open_end_game_ui(self):
        if self._end_game_open:
            return
        self.addobj(self.end_game_panel)
        self.end_game_text.setText(f"{world.points_highscore} points reached!")
        self._end_game_open = True

    def close_end_game_ui(self):
        if not self._end_game_open:
            return
        self.removeobj(self.end_game_panel)
        self._end_game_open = False

    def on_restart_clicked(self):
        self.close_end_game_ui()
        world.reset_game()
        full_pause_game()

    def on_main_menu_clicked(self):
        self.close_end_game_ui()
        world.reset_game()
        full_pause_game()
        self.manager.change_scene("main")

    #endregion

    def flip_settings(self):
        if self.settings_panel in self._objects:
            self.removeobj(self.settings_panel)
        else: 
            self.addobj(self.settings_panel) 

    def on_music_changed(self, value):
        save_manager.set_settings(musicSettings=value)
        setMusicVolume(value)

    def on_sfx_changed(self, value):
        save_manager.set_settings(sfxSettings=value)

    def on_difficulty_changed(self, value):
        save_manager.set_settings(difficulty=value)

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)

        player_health_comp = world.player_entity.get(HealthComponent)

        self.hp_bar.setValue(player_health_comp.current / player_health_comp.max)
        self.text_bar.setText(f"{player_health_comp.current} / {player_health_comp.max}")

        self.xp_bar.setValue(world.experience_current / world.experience_threshold)
        self.xp_bar_text.setText(f"{world.experience_current} / {world.experience_threshold}")

    def on_level_up_start(self, abilities):
        self.addobj(self.ability_layout_group)
        for index, ability_object in enumerate(self.ability_objects):
            ability_object.initialize(abilities[index])

    def on_level_up_end(self):
        self.removeobj(self.ability_layout_group)

class MainMenuScene(Scene):
    def __init__(self, manager):
        super().__init__(manager)

        self.title_text = StaticText(
            GAME_NAME,
            font_huge,
            (0,0),
            color=Color("#B85DC2")
        )

#region Main Screen 

        self.title_text.setPos((WIDTH / 2 - self.title_text.getSize()[0]/2, 24))
        self.addobj(self.title_text)

        main_buttons = LayoutGroup(LayoutType.vertical, 16, (32, HEIGHT / 2 - 96))

        self.start_button = Button(
            (0, 0, 128, 48),
            font,
            self.on_start_clicked,
            "Start!",
            end_game_ui,
            end_game_ui_hover,
            True,
            3,
            Color("#000000")
        )
        self.settings_button = Button(
            (0, 0, 128, 48),
            font,
            self.flip_settings,
            "Settings!",
            end_game_ui,
            end_game_ui_hover,
            True,
            3,
            Color("#000000")
        )
        self.tutorial_button = Button(
            (0, 0, 128, 48),
            font,
            self.flip_tutorial,
            "Tutorial!",
            end_game_ui,
            end_game_ui_hover,
            True,
            3,
            Color("#000000")
        )

        main_buttons.addToGroup(self.start_button)
        main_buttons.addToGroup(self.settings_button)
        main_buttons.addToGroup(self.tutorial_button)

        self.addobj(main_buttons)


        panel_pos = (WIDTH / 3, HEIGHT / 2 - 192)
        panel_size = (WIDTH / 2, HEIGHT - HEIGHT / 4)

        self.settings_panel = StaticImage(
            end_game_ui, panel_pos, size=panel_size, nineSliced=True, border=3
        )
        self.tutorial_panel = StaticImage(
            end_game_ui, panel_pos, size=panel_size, nineSliced=True, border=3
        )

        self._settings_open = False
        self._tutorial_open = False

#endregion

#region Settings 

        slider_x = 32
        slider_width = panel_size[0] - 64
        slider_height = 24

        self.music_label = StaticText("Music", font, (slider_x, 32), color=Color("#000000"))
        self.music_slider = UISlider(
            slider_x, 64, slider_width, slider_height,
            end_game_ui, 3,
            handleImage=end_game_ui_hover, handleWidth=16,
            currentValue=save_manager.musicSettings, maxValue=1.0,
            onChange=self.on_music_changed
        )

        self.sfx_label = StaticText("SFX", font, (slider_x, 112), color=Color("#000000"))
        self.sfx_slider = UISlider(
            slider_x, 144, slider_width, slider_height,
            end_game_ui, 3,
            handleImage=end_game_ui_hover, handleWidth=16,
            currentValue=save_manager.sfxSettings, maxValue=1.0,
            onChange=self.on_sfx_changed
        )

        self.difficulty_label = StaticText("Difficulty", font, (slider_x, 192), color=Color("#000000"))
        self.difficulty_slider = UISlider(
            slider_x, 224, slider_width, slider_height,
            end_game_ui, 3,
            handleImage=end_game_ui_hover, handleWidth=16,
            currentValue=save_manager.difficulty, maxValue=5.0,
            onChange=self.on_difficulty_changed
        )

        for settings_obj in (
            self.music_label, self.music_slider,
            self.sfx_label, self.sfx_slider,
            self.difficulty_label, self.difficulty_slider,
        ):
            self.settings_panel.addChild(settings_obj)

#endregion 

#region Tutorial 

        tutorial_strings = [
            "Use WASD or the arrow keys to move around.",
            "Kill enemies to receive experience points \nand level up.",
            "Receive more abilities and progress \nfurther and further.",
            "Good luck!"
        ]

        self._tutorial_strings = tutorial_strings
        self._tutorial_index = 0

        self.tutorial_text = StaticText(
            self._tutorial_strings[self._tutorial_index],
            font,
            (16, 32),
            color=Color("#000000")
        )
        self.tutorial_panel.addChild(self.tutorial_text)

        tutorial_nav = LayoutGroup(LayoutType.horizontal, 16, (32, panel_size[1] - 80))

        self.tutorial_prev_button = Button(
            (0, 0, 96, 40),
            font,
            self.on_tutorial_prev,
            "Back",
            end_game_ui,
            end_game_ui_hover,
            True,
            3,
            Color("#000000")
        )
        self.tutorial_next_button = Button(
            (0, 0, 96, 40),
            font,
            self.on_tutorial_next,
            "Next",
            end_game_ui,
            end_game_ui_hover,
            True,
            3,
            Color("#000000")
        )

        tutorial_nav.addToGroup(self.tutorial_prev_button)
        tutorial_nav.addToGroup(self.tutorial_next_button)

        self.tutorial_panel.addChild(tutorial_nav)

#endregion

    def flip_settings(self):
        if self._tutorial_open:
            self.removeobj(self.tutorial_panel)
            self._tutorial_open = False

        if self._settings_open:
            self.removeobj(self.settings_panel)
        else:
            self.addobj(self.settings_panel)
        self._settings_open = not self._settings_open

    def flip_tutorial(self):
        if self._settings_open:
            self.removeobj(self.settings_panel)
            self._settings_open = False

        if self._tutorial_open:
            self.removeobj(self.tutorial_panel)
        else:
            self.addobj(self.tutorial_panel)
        self._tutorial_open = not self._tutorial_open

    def on_music_changed(self, value):
        save_manager.set_settings(musicSettings=value)
        setMusicVolume(value)

    def on_sfx_changed(self, value):
        save_manager.set_settings(sfxSettings=value)

    def on_difficulty_changed(self, value):
        save_manager.set_settings(difficulty=value)

    def on_tutorial_prev(self):
        self._tutorial_index = max(0, self._tutorial_index - 1)
        self.tutorial_text.setText(self._tutorial_strings[self._tutorial_index])

    def on_tutorial_next(self):
        self._tutorial_index = min(len(self._tutorial_strings) - 1, self._tutorial_index + 1)
        self.tutorial_text.setText(self._tutorial_strings[self._tutorial_index])

    def on_start_clicked(self):
        self.move_scenes("gameplay")   

    def move_scenes(self, name):
        self.manager.change_scene(name)

sceneManager = SceneManager(
    scene_classes={
        "gameplay": GameplayScene, 
        "main": MainMenuScene, 
    }, 
    start_scene="main"
)

#endregion 

#region camera 

camera = Camera(WIDTH, HEIGHT, zoom=2.0)

#endregion

#region Input 

mouse_wheel_up = InputAction(
    bindings=[WheelBinding("up"), JoyButtonBinding(joystick, button=4)],
    on_trigger=lambda: change_zoom(False)   
)
mouse_wheel_down = InputAction(
    bindings=[WheelBinding("down"), JoyButtonBinding(joystick, button=5)],
    on_trigger=lambda: change_zoom(True)    
)

move_up = InputAction(bindings=[
    KeyBinding(pygame.K_w),
    KeyBinding(pygame.K_UP),
    JoyAxisBinding(joystick, axis=1, direction=-1),   
])
move_down = InputAction(bindings=[
    KeyBinding(pygame.K_s),
    KeyBinding(pygame.K_DOWN),
    JoyAxisBinding(joystick, axis=1, direction=1),
])
move_left = InputAction(bindings=[
    KeyBinding(pygame.K_a),
    KeyBinding(pygame.K_LEFT),
    JoyAxisBinding(joystick, axis=0, direction=-1),
])
move_right = InputAction(bindings=[
    KeyBinding(pygame.K_d),
    KeyBinding(pygame.K_RIGHT),
    JoyAxisBinding(joystick, axis=0, direction=1),
])

input_map = InputMap({mouse_wheel_down, mouse_wheel_up})

def change_zoom(lower: bool):
    old_zoom = camera.zoom

    if lower:
        if old_zoom <= MIN_ZOOM:
            return
        new_zoom = old_zoom - ZOOM_CHANGE
    else:
        if old_zoom >= MAX_ZOOM:
            return
        new_zoom = old_zoom + ZOOM_CHANGE

    center_x = camera.offset_x + (camera.screen_width / 2) / old_zoom
    center_y = camera.offset_y + (camera.screen_height / 2) / old_zoom

    camera.zoom = new_zoom

    camera.offset_x = center_x - (camera.screen_width / 2) / new_zoom
    camera.offset_y = center_y - (camera.screen_height / 2) / new_zoom

#endregion 

#region Main  

PAUSED = False 
FULLPAUSE = False 

DEBUG_GRID = False
DEBUG_FPS = False 
DEBUG_POS = False 
DEBUG_TIME = False
DEBUG_POINTS = False 

FPS_TEXT_COLOR = (255, 255, 255)
FPS_MARGIN = 10

def format_time(seconds: float) -> str:
    minutes, secs = divmod(int(seconds), 60)
    return f"{minutes:02d}:{secs:02d}"

async def main():
    running = True
    music_started = False
    while running:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            if not music_started and event.type in (pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN):
                playBgm()
                music_started = True

        input_map._update(events)

        dt = clock.tick(FPS) / 1000.0
        screen.fill((25, 25, 35))

        if type(sceneManager.current_scene) is GameplayScene:
            if not PAUSED:
                world.update(dt, save_manager.get_settings())
                player_control_system(world.player_entity, events, move_up, move_down, move_left, move_right, dt)
                enemy_system(world)
                movement_system(world, dt)
                emitting_system(world, dt, joystick)
                projectile_system(world, world.projectile_pool, dt)
                animation_system(world, dt)          
                grid = build_spatial_grid(world.entities, CELL_SIZE)
                collision_system(grid, world, collect_sounds)
                health_system(world)
                death_system(world)                 
                text_spawning_system(world)

            sceneManager.update(dt)
            sceneManager.handle_events(events)

            render_system(world, screen, camera)
            if not PAUSED:
                damage_text_system(world, screen,camera,atlas,dt)
                camera_follow_system(world.player_entity, camera, SMOOTH_SPEED, dt)
            sceneManager.draw(screen)

            if DEBUG_GRID:
                render_spatial_grid(screen, grid, CELL_SIZE, camera)
            if DEBUG_TIME:
                time_surface = font.render(f"Time: {format_time(world.time)}", True, FPS_TEXT_COLOR)
                screen.blit(time_surface, (FPS_MARGIN, HEIGHT - time_surface.get_height() - FPS_MARGIN * 4))
            if DEBUG_FPS:
                fps_surface = font.render(f"FPS: {clock.get_fps():.0f}", True, FPS_TEXT_COLOR)
                screen.blit(fps_surface, (FPS_MARGIN, HEIGHT - fps_surface.get_height() - FPS_MARGIN))
            if DEBUG_POS:
                pos_surface = font.render(f"{world.player_entity.get(MovementComponent).pos}", True, FPS_TEXT_COLOR)
                screen.blit(pos_surface, (FPS_MARGIN, HEIGHT - pos_surface.get_height() - FPS_MARGIN *2.5))
            if DEBUG_POINTS:
                pos_surface = font.render(f"Points: {world.points}, bracked: {world.progression.current_point_bracket}", True, FPS_TEXT_COLOR)
                screen.blit(pos_surface, (FPS_MARGIN, HEIGHT - pos_surface.get_height() - FPS_MARGIN *2.5))
        else:
            sceneManager.update(dt)
            sceneManager.handle_events(events)
            sceneManager.draw(screen)

        sound_system(world, save_manager.sfxSettings)

        pygame.display.flip()
        world.clear_frame_events()
        await asyncio.sleep(0)

    pygame.quit()

asyncio.run(main())

#endregion