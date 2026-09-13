import random

from general.entity import *
from components.emitting import *
from components.movement import *
from components.health import *

from abilities.ability_definition import *


class AbilityResolver:

    def __init__(self, abilityLib: AbilityLibrary, world):
        self.ability_library = abilityLib
        self.world = world

        self.player_abilities: list[PlayerAbility] = []
        self.available_abilities: list[PlayerAbility] = []
        self.three_abilities: list[PlayerAbility] = []
        self.buffer: list[PlayerAbility] = []

        self.build_available_dict()

    def restart(self):
        self.player_abilities.clear()
        self.available_abilities.clear()
        self.three_abilities.clear()
        self.buffer.clear()
        self.build_available_dict()

    def build_available_dict(self):
        self.available_abilities.clear()
        for ability in self.ability_library.all_abilities:
            if ability in self.player_abilities:
                continue
            if any(dep not in self.player_abilities for dep in ability.dependant_on):
                continue
            if any(excl in self.player_abilities for excl in ability.excludes):
                continue
            self.available_abilities.append(ability)

    def get_random_abilities(self) -> list[PlayerAbility]:
        self.three_abilities.clear()
        self.buffer.clear()
        self.buffer.extend(self.available_abilities)

        while self.buffer and len(self.three_abilities) < 3:
            random_index = random.randint(0, len(self.buffer) - 1)
            self.three_abilities.append(self.buffer.pop(random_index))

        if len(self.three_abilities) < 3 and self.ability_library.repeatable_abilities:
            repeat_pool = list(self.ability_library.repeatable_abilities)
            while len(self.three_abilities) < 3:
                if not repeat_pool:
                    repeat_pool = list(self.ability_library.repeatable_abilities)
                random_index = random.randint(0, len(repeat_pool) - 1)
                self.three_abilities.append(repeat_pool.pop(random_index))

        return self.three_abilities
    
    def grant_starting_abilities(self):
        for ab in self.ability_library.starting_abilities:
            if ab not in self.player_abilities:
                self.player_abilities.append(ab)
            self.resolve_effects(ab)
        self.build_available_dict()

    def on_ability_selected(self, ability_selected: PlayerAbility):
        is_curated_pick = ability_selected in self.available_abilities
        if is_curated_pick:
            self.player_abilities.append(ability_selected)
            self.available_abilities.remove(ability_selected)
            self.build_available_dict()

        self.resolve_effects(ability_selected)

    #region Ability Execution

    def resolve_effects(self, ab: PlayerAbility):
        for effect in ab.effects:
            match effect:
                case AddEmitter():
                    self.add_emitter(effect)
                case ModifyEmitter():
                    self.modify_emitter(ab, effect)
                case RemoveAbility():
                    self.remove_abilities(effect)
                case StatChange():
                    self.apply_stat_change(effect)

    def add_emitter(self, effect: AddEmitter):
        e = Entity()
        e.add(EmitterComponent(
            effect.emitter_id, effect.definition, effect.type,
            effect.time_between_shots, self.world.player_entity,
        ))
        self.world.addEntity(e)
        self.world.register_emitter(effect.emitter_id, e)

    def modify_emitter(self, ability: PlayerAbility, effect: ModifyEmitter):
        entity = self.world.get_emitter_entity(effect.target_emitter_id)
        if not entity:
            raise RuntimeError(f"tried modifying unknown emitter '{effect.target_emitter_id}'")

        emitter = entity.get(EmitterComponent)
        emitter.add_modifiers(ability._name, effect.modifiers, effect.emission_type_override)

    def remove_abilities(self, effect: RemoveAbility):
        for ab in effect.abilities_to_remove:
            if ab in self.player_abilities:
                self.player_abilities.remove(ab)
                self.undo_effects(ab)
        self.build_available_dict()

    def undo_effects(self, ability: PlayerAbility):
        for effect in ability.effects:
            match effect:
                case AddEmitter():
                    self.world.remove_emitter(effect.emitter_id)
                case ModifyEmitter():
                    entity = self.world.get_emitter_entity(effect.target_emitter_id)
                    if entity:
                        entity.get(EmitterComponent).remove_modifiers_from(ability._name)
                case StatChange():
                    self.apply_stat_change(effect, reverse=True)

    def apply_stat_change(self, effect: StatChange, reverse: bool = False):
        player = self.world.player_entity
        movement, health = player.get(MovementComponent), player.get(HealthComponent)

        if not (movement and health):
            raise RuntimeError("tried giving stat buff to a player without necessary components")

        sign = -1 if reverse else 1
        if effect.speed_change != 0.0:
            movement.speed += sign * effect.speed_change
        if effect.health_change != 0.0:
            health.max += sign * effect.health_change
            health.current += sign * effect.health_change

    #endregion