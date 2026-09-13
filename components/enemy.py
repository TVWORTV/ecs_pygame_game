

class EnemyComponent:
    __slots__ = ("target", "damage_on_hit", "experience_on_death")   
    def __init__(self, target, damage_on_hit, experience_on_death : int = 5):
        self.target = target
        self.damage_on_hit = damage_on_hit  
        self.experience_on_death = experience_on_death
