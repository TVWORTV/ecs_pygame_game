


class PlayerComponent: 
    __slots__ = ("damage_timer", "time_between_damages")

    def __init__(self, time_between_damages):
        self.damage_timer = -0.1
        self.time_between_damages = time_between_damages
