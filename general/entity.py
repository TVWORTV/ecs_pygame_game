

class Entity:
    _next_id = 0

    def __init__(self):
        self.id = Entity._next_id
        Entity._next_id += 1

        self.active = True 
        self.components = {}

    def deactivate(self):
        self.active = False

    def add(self, component):
        self.components[type(component)] = component
        return self

    def get(self, component_type):
        return self.components.get(component_type)
