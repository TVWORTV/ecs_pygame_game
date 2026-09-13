from enum import Enum, auto 
from typing import Literal

class Rotation(Enum):
    LEFT = auto()
    UP = auto()
    RIGHT = auto()
    DOWN = auto()

class SpecialRenderingComponent:
    __slots__ = (
        "flips_with_direction", 
        "rotates_with_direction", 
        "flips_with_mouse", 

        "original_orientation_x", 
        "original_rotation_angle"
        )

    def __init__(
            self, 
            flips_with_dir : bool = False, 
            rotates_with_dir : bool = False, 
            original_rotation : Rotation = Rotation.UP, 
            original_orientation: Literal[Rotation.LEFT, Rotation.RIGHT] = Rotation.LEFT
            ):
        self.flips_with_direction = flips_with_dir
        self.rotates_with_direction = rotates_with_dir
        self.original_orientation_x = original_orientation 
        self.original_rotation_angle = original_rotation
