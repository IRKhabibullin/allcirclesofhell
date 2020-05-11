from typing import List, TYPE_CHECKING, Dict, Tuple

from game.mechanics.constants import slotObstacle, slotHero, slotUnit
from game.models import HeroModel, BaseUnitModel, AbilityModel

if TYPE_CHECKING:
    from django.db import models
    from game.mechanics.board import Hex


class BaseGameObject:
    def __init__(self, **kwargs):
        self.position: Hex = kwargs.get('position', None)


class Obstacle(BaseGameObject):
    def __str__(self):
        return slotObstacle


class InteractiveGameObject(BaseGameObject):
    def __init__(self, object_model: 'models.Model', **kwargs):
        super().__init__(**kwargs)
        self._object: models.Model = object_model


class BaseUnitObject(InteractiveGameObject):
    def __init__(self, object_model: BaseUnitModel, **kwargs):
        super().__init__(object_model, **kwargs)
        self.moves: list = []
        self.attack_hexes: list = []
        self.enemy_target: str = slotHero
        self.actions = [
            'move',
            'attack',
            *[spell.code_name for spell in self._object.spells.all()],
        ]
        self.ability_map = {
            'spell': self._object.spells,
            'skill': self._object.skills,
            'item': self._object.items
        }
        self.unsaved_abilities = {
            'spell': [],
            'skill': [],
            'item': [],
        }

    @property
    def name(self):
        return self._object.name

    @property
    def health(self):
        return self._object.health

    @property
    def damage(self):
        return self._object.damage

    @property
    def attack_range(self):
        return self._object.attack_range

    @property
    def move_range(self):
        return self._object.move_range

    @property
    def armor(self):
        return self._object.armor

    @property
    def skills(self):
        return self._object.skills

    @property
    def spells(self):
        return self._object.spells

    @property
    def img_path(self):
        return self._object.img_path

    def has_spell(self, spell_code_name):
        return bool(self.spells.filter(code_name=spell_code_name))

    def choose_action(self, available_actions: 'Dict[str, List[Hex]]'):
        action_name, target_hex = self._get_best_action(available_actions)
        action_request = {'action': action_name, 'source': self, 'target_hex': target_hex}
        print(f'unit {self._object.name} chooses action {action_request}')
        return action_request

    def _get_best_action(self, available_actions: 'Dict[str, List[Hex]]') -> Tuple[str, str]:
        best_action: str = list(available_actions.keys())[0]
        best_target: Hex = available_actions[best_action][0]
        for action, action_targets in available_actions.items():
            for target in action_targets:
                if str(target.slot) == self.enemy_target:
                    best_action, best_target = action, target
        return best_action, best_target.id

    def add_ability(self, ability_type: str, ability: AbilityModel):
        self.ability_map[ability_type].add(ability)
        self.unsaved_abilities[ability_type].append(ability)

    def remove_unsaved_abilities(self):
        for ability_type in self.unsaved_abilities:
            if self.unsaved_abilities[ability_type]:
                [self._object.spells.remove(ability) for ability in self.unsaved_abilities[ability_type]]

    def keep_unsaved_abilities(self):
        for ability_type in self.unsaved_abilities:
            self.unsaved_abilities[ability_type].clear()

    def receive_damage(self, damage):
        self._object.health -= damage

    def set_health(self, health):
        self._object.health = health


class Hero(BaseUnitObject):

    def __init__(self, object_model: HeroModel, **kwargs):
        super().__init__(object_model, **kwargs)
        self.enemy_target: str = slotUnit

    def __str__(self):
        return slotHero


class Unit(BaseUnitObject):
    def __str__(self):
        return slotUnit

    @property
    def pk(self):
        return self._object.pk

    @property
    def level(self):
        return self._object.level
