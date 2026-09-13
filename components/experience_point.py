

class ExperiencePointComponent: 
    __slots__ = ("value")

    def __init__(self, value):
        self.set_params( value)

    def set_params(self, value : int):
        self.value = value 