from typing import Final
import pygame 

GAME_NAME : Final[str] = "SWARM INCOMING"
MUSIC_DEFAULT: Final[float] = 0.15 
SFX_DEFAULT: Final[float] = 0.5 

WIDTH : Final[int] = 960
HEIGHT : Final[int] = 540

UI_SCALE : Final[float] = 3.0

SMOOTH_SPEED : Final[float] = 3

TOP_LEFT_MOVEMENT_LIMIT : Final[pygame.Vector2] = pygame.Vector2(300, 150) 
BOTTOM_RIGHT_MOVEMENT_LIMIT : Final[pygame.Vector2] = pygame.Vector2(1750, 950) 

ZOOM_CHANGE : Final[float] = 0.1
MIN_ZOOM : Final[float] = 1.0
MAX_ZOOM : Final[float] = 3.0

DAMAGE_TEXT_SPEED : Final[float] = 40.0
DAMAGE_TEXT_LIFETIME : Final[float] = 0.6

TIME_BETWEEN_PLAYER_DAMAGES : Final[float] = 0.2

#region game defaults 

PLAYER_SPEED_DEFAULT : Final[float] = 125.0 
ENEMY_SPEED_DEFAULT : Final[float] = 75.0 

PLAYER_HEALTH_DEFAULT : Final[int] = 30 
ENEMY_HEALTH_DEFAULT : Final[int] = 23

PLAYER_DAMAGE_DEFAULT : Final[int] = 5
ENEMY_DAMAGE_DEFAULT : Final[int] = 4

PROJECTILE_SPEED_DEFAULT : Final[float] = 95.0 

#endregion

#region Spawning 

ENEMY_SPAWN_AREA : Final[pygame.Vector2] = pygame.Vector2(800.0, 850.0) 

#endregion 

#region Progression 

POINTS_PER_SECOND : Final[int] = 2

SPAWN_INTERVAL_DEFAULT : Final[float] = 1.0

POINT_ON_DEATH : Final[int] = 5

#endregion

#region Experience 

EXPERIENCE_AMOUNT_BASE : Final[int] = 5

EXPERIENCE_THRESHOLD_BASE : Final[int] = 15

EXPERIENCE_INCREASE_MULTIPLIER : Final[float] = 1.3

ABILITY_NAME_COLOR : Final[str] = "#231606"
ABILITY_DESC_COLOR : Final[str] = "#231606"

#endregion 

#region Settings 

MIN_DIFFICULTY : Final[int] = 1 
MAX_DIFFICULTY : Final[int] = 5 
DEFAULT_DIFFICULTY : Final[int] = 2

DIFFICULTY_ENEMY_SPEED_CHANGE : Final[float] = 5.0 
DIFFICULTY_ENEMY_SIZE_CHANGE : Final[float] = 0.1 
DIFFICULTY_ENEMY_DAMAGE_CHANGE : Final[int] = 3 
DIFFICULTY_ENEMY_HEALTH_CHANGE : Final[int] = 5 

#endregion 
