

class Collider:
    __slots__ = ("radius","can_collide")
    def __init__(self, radius=16.0):
        self.radius = radius
        self.can_collide = True 

    def reset(self, size):
        self.can_collide = True 
        self.radius = size