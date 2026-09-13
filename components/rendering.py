import pygame

class RenderingComponent:
    __slots__ = ("image", "offset", "flip_x", "angle", "layer", "z_index")
    def __init__(self, image=None, offset=(0, 0), flip_x=False, layer=0, z_index=None):
        self.image = image
        self.offset = pygame.Vector2(offset)
        self.flip_x = flip_x
        self.angle = 0
        self.layer = layer
        self.z_index = z_index

    def reset(self):
        self.offset = pygame.Vector2(0, 0)
        self.flip_x = False