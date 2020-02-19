"""
Functions for actions
"""
from collections import defaultdict
from typing import List, Dict, TYPE_CHECKING

from game.models import SpellModel
from game.mechanics.constants import slotEmpty, slotObstacle
from game.mechanics.game_objects import Hero, BaseGameObject, BaseUnitObject

if TYPE_CHECKING:
    from game.mechanics.game_instance import GameInstance
    from game.mechanics.board import Hex


class ActionResponse:
    def __init__(self, name: str):
        self.name: str = name
        self.state: str = 'success'
        # actions made by units
        self.hero_actions: Dict[str: list] = {}
        self.units_actions: Dict[Dict[str: list]] = defaultdict(dict)

    def to_dict(self):
        return {'action': self.name, 'state': self.state, 'hero_actions': self.hero_actions,
                'units_actions': self.units_actions}


class Action:
    """Base class for all game actions"""
    action_name: str

    def __init__(self, game: 'GameInstance', action_data: dict):
        self.game = game
        self.source: BaseGameObject = action_data['source']
        self.target_hex: str = action_data['target_hex']

    @classmethod
    def available_targets(cls, game: 'GameInstance', unit: 'BaseUnitObject') -> 'List[Hex]':
        raise NotImplementedError

    def execute(self) -> Dict[str, List]:
        """Main method to execute action"""
        raise NotImplementedError


class SpellAction(Action):
    """Base class for all spell actions"""
    action_name: str

    def __init__(self, game: 'GameInstance', action_data: dict):
        if not isinstance(action_data['source'], BaseUnitObject):
            raise RuntimeError(f'This game object is muggle')
        super().__init__(game, action_data)
        try:
            self.spell = self.source.spells.get(code_name=self.action_name)
        except SpellModel.DoesNotExist:
            raise RuntimeError('Action not allowed')
        self.spell_effects = {item.effect.code_name: item.value for item in self.spell.spelleffectmodel_set.all()}

    def execute(self) -> Dict[str, List]:
        raise NotImplementedError


class Idle(Action):
    """Idle action. Unit does nothing"""
    action_name = 'idle'

    def __init__(self, game: 'GameInstance', action_data):
        if not isinstance(action_data['source'], BaseUnitObject):
            raise RuntimeError(f'This game object can not perform action {self.action_name}')
        super().__init__(game, action_data)

    @classmethod
    def available_targets(cls, game: 'GameInstance', unit: 'BaseUnitObject'):
        return [unit.position.id]

    def execute(self) -> Dict[str, List]:
        return {}


class MoveAction(Action):
    """Simple move"""
    action_name = 'move'

    def __init__(self, game: 'GameInstance', action_data):
        if not isinstance(action_data['source'], BaseUnitObject):
            raise RuntimeError(f'This game object can not perform action {self.action_name}')
        super().__init__(game, action_data)

    @classmethod
    def available_targets(cls, game: 'GameInstance', unit: 'BaseUnitObject'):
        targets = game.get_hexes_in_range(unit.position, unit.move_range, allowed=[slotEmpty])
        return list(targets.values())

    def execute(self) -> Dict[str, List]:
        if self.game.distance(self.source.position, self.target_hex) <= self.source.move_range:
            self.game.move_object(self.source, self.target_hex)
            return {}
        raise RuntimeError('Cant move there')


class Attack(Action):
    """Simple attack"""
    action_name = 'attack'

    def __init__(self, game: 'GameInstance', action_data):
        if not isinstance(action_data['source'], BaseUnitObject):
            raise RuntimeError(f'This game object can not perform action {self.action_name}')
        super().__init__(game, action_data)

    @classmethod
    def available_targets(cls, game: 'GameInstance', unit: 'BaseUnitObject'):
        targets = game.get_hexes_in_range(unit.position, unit.attack_range, allowed=[str(unit.priority_target)])
        return list(targets.values())

    def execute(self) -> Dict[str, List]:
        if self.game.distance(self.source.position, self.target_hex) <= self.source.attack_range:
            self.game.deal_damage(self.target_hex, self.source.damage)
            return {self.action_name: [{'target_hex': self.target_hex, 'damage': self.source.damage}]}
        raise RuntimeError('Cant attack target. Its too far')


class RangeAttack(Action):
    """Simple range attack"""
    action_name = 'range_attack'

    def __init__(self, game: 'GameInstance', action_data):
        if not isinstance(action_data['source'], BaseUnitObject):
            raise RuntimeError(f'This game object can not perform action {self.action_name}')
        super().__init__(game, action_data)

    @classmethod
    def available_targets(cls, game: 'GameInstance', unit: 'BaseUnitObject'):
        targets = game.get_hexes_in_range(unit.position, unit.attack_range + 1, allowed=[str(unit.priority_target)])
        return list(targets.values())

    def execute(self) -> Dict[str, List]:
        if self.game.distance(self.source.position, self.target_hex) <= self.source.attack_range + 1:
            self.game.deal_damage(self.target_hex, self.source.damage)
            return {self.action_name: [{'target_hex': self.target_hex, 'damage': self.source.damage}]}
        raise RuntimeError('Cant attack target. Its too far')
    

class PathOfFire(SpellAction):
    """Path of fire spell"""
    action_name = 'path_of_fire'

    def __init__(self, game, action_data):
        super().__init__(game, action_data)

    @classmethod
    def available_targets(cls, game: 'GameInstance', unit: 'BaseUnitObject') -> 'List[Hex]':
        try:
            spell = unit.spells.get(code_name=PathOfFire.action_name)
        except SpellModel.DoesNotExist:
            raise RuntimeError('Action not allowed')
        spell_effects = {item.effect.code_name: item.value for item in spell.spelleffectmodel_set.all()}
        targets = game.get_hexes_in_range(unit.position, spell_effects['radius'], restricted=[slotObstacle]).values()
        targets = [_hex for _hex in targets if unit.position != _hex]
        return targets

    def execute(self) -> Dict[str, List]:
        if self.game.distance(self.source.position, self.target_hex) > self.spell_effects['radius']:
            raise RuntimeError('Target is too far')

        action_steps: list = []
        print('target hex', self.target_hex)
        q, r = map(int, self.target_hex.split(';'))
        dq, dr = q - self.source.position.q, r - self.source.position.r
        for i in range(int(self.spell_effects['path_length'])):
            hex_id = f"{q + dq * i};{r + dr * i}"
            if str(self.game.get_object_by_position(hex_id)) == slotObstacle:
                break
            self.game.deal_damage(hex_id, self.spell_effects['damage'])
            action_steps.append({'target_hex': hex_id, 'damage': self.spell_effects['damage']})
        return {self.action_name: action_steps}


class ShieldBash(SpellAction):
    """Shield bash spell"""
    action_name = 'shield_bash'

    def __init__(self, game, action_request):
        super().__init__(game, action_request)
        if self.game.board.distance(self.game.hero.position, self.target_hex) > self.spell_effects['radius']:
            raise ActionNotAllowedError

    def execute(self):
        action_result = {'target_hex': self.target_hex.id}
        target_hexes = list(set(self.game.board.get_hexes_in_range(self.target_hex, 1)).intersection(
            self.game.board.get_hexes_in_range(self.game.hero.position, 1)) - {self.game.hero.position.id})
        targets = {_unit.pk: {} for _unit in self.game.units.values() if _unit.position.id in target_hexes}
        for _unit_id in targets:
            _unit = self.game.units[_unit_id]
            dq, dr = _unit.position.q - self.game.hero.position.q, _unit.position.r - self.game.hero.position.r
            hex_behind_id = f"{_unit.position.q + dq};{_unit.position.r + dr}"
            hex_behind = self.game.board.get(hex_behind_id)
            if not hex_behind or hex_behind.occupied_by != slotEmpty:
                # if no hex behind bashed unit or hex behind is occupied, then damage is doubled
                targets[_unit_id]['damage'] = self.spell_effects['damage'] * 2
            else:
                # if hex behind is empty, then bashed unit is pushed back at this empty hex
                targets[_unit_id]['damage'] = self.spell_effects['damage']
                self.game.board.place_game_object(_unit, hex_behind_id)
            self.game.damage_instance(self.game.hero, _unit, targets[_unit_id]['damage'])
        action_result['target_units'] = targets
        action_result['stunned_units'] = list(targets.keys())
        return action_result


class Blink(SpellAction):
    """Blink spell"""
    action_name = 'blink'

    def __init__(self, game, action_request):
        super().__init__(game, action_request)
        if self.target_hex.occupied_by != slotEmpty:
            raise ActionNotAllowedError
        if self.game.board.distance(self.game.hero.position, self.target_hex) > self.spell_effects['radius']:
            raise ActionNotAllowedError

    def execute(self):
        self.game.board.place_game_object(self.game.hero, self.target_hex.id)
        return {}


class ActionManager:
    """Class to manage all actions"""
    _actions: Dict[str, Action.__class__] = {
        'idle': Idle,
        'move': MoveAction,
        'attack': Attack,
        'range_attack': RangeAttack,
        'path_of_fire': PathOfFire,
        'shield_bash': ShieldBash,
        'blink': Blink,
    }

    _common_actions = {
        'move': MoveAction,
        'attack': Attack,
    }
    _hero_actions = {
        'range_attack': RangeAttack
    }
    _spells = {
        'path_of_fire': PathOfFire,
        'shield_bash': ShieldBash,
        'blink': Blink,
    }

    @staticmethod
    def has_action(acting_object, action_name):
        if action_name in ActionManager._common_actions:
            return True
        if isinstance(acting_object, Hero):
            if action_name in ActionManager._hero_actions:
                return True
            # check for spells
            if action_name in ActionManager._spells:
                if acting_object.has_spell(action_name):
                    return True
        return False

    @classmethod
    def get_action(cls, game: 'GameInstance', action_data: dict) -> Action:
        if action_data['action'] in cls._actions:
            action = cls._actions[action_data['action']](game, action_data)
            return action
        raise RuntimeError('No such action')

    @classmethod
    def available_actions(cls, game: 'GameInstance', unit: 'BaseUnitObject') -> 'Dict[str, List[Hex]]':
        # calculate actions available for unit
        available_actions: Dict[str, List[Hex]] = {}
        for action in unit.actions:
            targets = cls._actions[action].available_targets(game, unit)
            if targets:
                available_actions[action] = targets
        return available_actions
