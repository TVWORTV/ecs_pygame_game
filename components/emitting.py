import dataclasses
from dataclasses import dataclass
from enum import Enum, auto

from data_and_definitions.projectile_definition import *
from general.entity import *

TIME_BETWEEN_SHOTS = "time_between_shots"  

class emitting_type(Enum):
    AT_TARGET = auto()
    AHEAD = auto()
    CLOSEST = auto()
    BEHIND = auto()


class ModifierOp(Enum):
    ADD = auto()
    MULTIPLY = auto()
    SET = auto()


@dataclass(frozen=True)
class StatModifier:
    field: str
    operation: ModifierOp
    value: float


class EmitterComponent:
    __slots__ = (
        "emitter_id",
        "base_definition", "base_emission_type", "base_time_between_shots",
        "modifiers",
        "definition", "emission_type", "time_between_shots",  
        "timer", "owner",
    )

    def __init__(
        self,
        emitter_id: str,
        definition: projectile_definition,
        emission_type: emitting_type,
        time_between_shots: float,
        owner: Entity,
    ):
        self.emitter_id = emitter_id
        self.base_definition = definition
        self.base_emission_type = emission_type
        self.base_time_between_shots = time_between_shots
        self.modifiers: list[tuple[str, StatModifier]] = []
        self.owner = owner
        self.timer = time_between_shots
        self._recompute()

    def add_modifiers(
        self,
        source_ability_name: str,
        modifiers: list[StatModifier],
        emission_type_override: "emitting_type | None" = None,
    ):
        for m in modifiers:
            self.modifiers.append((source_ability_name, m))
        if emission_type_override is not None:
            self.base_emission_type = emission_type_override
        self._recompute()

    def remove_modifiers_from(self, source_ability_name: str):
        self.modifiers = [(src, m) for src, m in self.modifiers if src != source_ability_name]
        self._recompute()

    def _recompute(self):
        additive: dict[str, float] = {}
        multiplicative: dict[str, float] = {}
        sets: dict[str, float] = {}
        time_between_shots = self.base_time_between_shots

        for _, mod in self.modifiers:
            if mod.field == TIME_BETWEEN_SHOTS:
                if mod.operation == ModifierOp.ADD:
                    time_between_shots += mod.value
                elif mod.operation == ModifierOp.MULTIPLY:
                    time_between_shots *= mod.value
                elif mod.operation == ModifierOp.SET:
                    time_between_shots = mod.value
                continue

            if mod.operation == ModifierOp.ADD:
                additive[mod.field] = additive.get(mod.field, 0.0) + mod.value
            elif mod.operation == ModifierOp.MULTIPLY:
                multiplicative[mod.field] = multiplicative.get(mod.field, 1.0) * mod.value
            elif mod.operation == ModifierOp.SET:
                sets[mod.field] = mod.value

        new_def = dataclasses.replace(self.base_definition)
        for f, v in additive.items():
            setattr(new_def, f, getattr(new_def, f) + v)
        for f, v in multiplicative.items():
            setattr(new_def, f, getattr(new_def, f) * v)
        for f, v in sets.items():
            setattr(new_def, f, v)

        self.definition = new_def
        self.emission_type = self.base_emission_type
        self.time_between_shots = max(0.01, time_between_shots)

    def reset(self):
        self.timer = 0.0
        self.base_time_between_shots = 0.0
        self.base_definition = None
        self.base_emission_type = None
        self.modifiers = []
        self.definition = None
        self.emission_type = None
        self.time_between_shots = 0.0
        self.owner = None