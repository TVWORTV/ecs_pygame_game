from dataclasses import dataclass, field
from data_and_definitions.projectile_definition import *
from components.emitting import *


@dataclass
class AbilityLibrary:
    all_abilities: list["PlayerAbility"] = field(default_factory=list)
    repeatable_abilities: list["PlayerAbility"] = field(default_factory=list)
    starting_abilities: list["PlayerAbility"] = field(default_factory=list)
    

@dataclass
class PlayerAbility:
    _name: str
    _description: str

    dependant_on: list["PlayerAbility"] = field(default_factory=list)  
    excludes: list["PlayerAbility"] = field(default_factory=list)      
    effects: list["AbilityEffect"] = field(default_factory=list)


#region effects

@dataclass
class AbilityEffect:
    pass


@dataclass
class AddEmitter(AbilityEffect):
    emitter_id: str
    definition: projectile_definition
    type: emitting_type
    time_between_shots: float


@dataclass
class ModifyEmitter(AbilityEffect):
    target_emitter_id: str
    modifiers: list[StatModifier] = field(default_factory=list)
    emission_type_override: emitting_type | None = None


@dataclass
class RemoveAbility(AbilityEffect):
    abilities_to_remove: list[PlayerAbility] = field(default_factory=list)


@dataclass
class StatChange(AbilityEffect):
    speed_change: float = 0
    base_damage_change: float = 0
    base_lifetime_change: float = 0
    health_change: int = 0

#endregion