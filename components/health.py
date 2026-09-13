class HealthComponent:
    __slots__ = ("current", "max", "invincibility_timer", "dying")

    def __init__(self, max):
        self.current = self.max = max
        self.invincibility_timer = -1.0
        self.dying = False

    def reset(self):
        self.current = self.max = 0

    def respawn(self):
        self.dying = False