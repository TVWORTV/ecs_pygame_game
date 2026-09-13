from dataclasses import dataclass
from consts import *
from data_and_definitions.enemy_definition import *

@dataclass
class TimeProgressionBracket:
    min_sec_required : int 
    spawn_interval : float = SPAWN_INTERVAL_DEFAULT  

@dataclass 
class PointProgressionBracket:
    points_required : int 
    enemies_available : list[enemy_definition] 

@dataclass
class WorldProgression:

    time_brackets : list[TimeProgressionBracket] 
    point_brackets : list[PointProgressionBracket] 

    current_time_bracket : int = 0 
    current_point_bracket : int = 0 
    
    def reset(self):
        self.current_time_bracket = 0 
        self.current_point_bracket = 0 

    def check_time(self, time):
        next_bracket = self.current_time_bracket + 1
        if next_bracket >= len(self.time_brackets):
            return  
        if time > self.time_brackets[next_bracket].min_sec_required:
            self.current_time_bracket = next_bracket

    def check_points(self, points):
        next_bracket = self.current_point_bracket + 1
        if next_bracket >= len(self.point_brackets):
            return  
        if points > self.point_brackets[next_bracket].points_required:
            self.current_point_bracket = next_bracket

    def spawn_interval(self) -> float:
        return self.time_brackets[self.current_time_bracket].spawn_interval

    def enemies_available(self) -> list[enemy_definition]:
        return self.point_brackets[self.current_point_bracket].enemies_available