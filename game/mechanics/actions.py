"""
Functions for actions
"""
from collections import defaultdict
from typing import List, Dict, TYPE_CHECKING

from game.models import SpellModel
from game.mechanics.constants import slotEmpty, slotObstacle, slotUnit
from game.mechanics.game_objects import Hero, BaseGameObject, BaseUnitObject

if TYPE_CHECKING:
    from game.mechanics.game_instance import GameInstance
    from game.mechanics.board import Hex


class ActionResponse:
    def __init__(self, name: str):
        self.name: str = name
        self.state: str = 'success'
        # additional info about game objects
        self.hero_data: dict = {}
        self.units_data: dict = defaultdict(dict)

    def to_dict(self):
        return {'action': self.name, 'state': self.state, 'hero_data': self.hero_data, 'units_data': self.units_data}


class ActionNotAllowedError(Exception):
    """Exception raised when action could not be executed"""
    pass


class Action:
    """Base class for all game actions"""
    action_name: str

    def __init__(self, game: 'GameInstance', action_data):
        self.game = game
        self.source: BaseGameObject = action_data['source']
        self.target_hex: str = action_data['target_hex']

    @staticmethod
    def available_targets(game: 'GameInstance', unit: 'BaseUnitObject'):
        return False

    def execute(self):
        """Main method to execute action"""
        raise NotImplementedError


class SpellAction(Action):
    """Base class for all spell actions"""
    action_name: str

    def __init__(self, game, action_request):
        super().__init__(game, action_request)
        try:
            self.spell = self.game.hero.spells.get(code_name=self.action_name)
        except SpellModel.DoesNotExist:
            raise ActionNotAllowedError
        self.spell_effects = {item.effect.code_name: item.value for item in self.spell.spelleffect_set.all()}

    def execute(self):
        raise NotImplementedError


class Idle(Action):
    """Idle action. Unit does nothing"""
    action_name = 'idle'

    def __init__(self, game: 'GameInstance', action_data):
        if not isinstance(action_data['source'], BaseUnitObject):
            raise RuntimeError(f'This game object can not perform action {self.action_name}')
        super().__init__(game, action_data)

    @staticmethod
    def available_targets(game: 'GameInstance', unit: 'BaseUnitObject'):
        return [unit.position.id]

    def execute(self):
        pass


class MoveAction(Action):
    """Simple move"""
    action_name = 'move'

    def __init__(self, game: 'GameInstance', action_data):
        if not isinstance(action_data['source'], BaseUnitObject):
            raise RuntimeError(f'This game object can not perform action {self.action_name}')
        super().__init__(game, action_data)

    @staticmethod
    def available_targets(game: 'GameInstance', unit: 'BaseUnitObject'):
        targets = game.get_hexes_in_range(unit.position, unit.move_range, allowed=[slotEmpty])
        return list(targets.values())

    def execute(self):
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

    @staticmethod
    def available_targets(game: 'GameInstance', unit: 'BaseUnitObject'):
        targets = game.get_hexes_in_range(unit.position, unit.attack_range, allowed=[str(unit.priority_target)])
        return list(targets.values())

    def execute(self):
        if self.game.distance(self.source.position, self.target_hex) <= self.source.attack_range:
            self.game.deal_damage(self.source, self.target_hex, self.source.damage)
            return {'action': self.action_name, 'target_hex': self.target_hex, 'damage': self.source.damage}
        raise RuntimeError('Cant attack target. Its too far')


class RangeAttack(Action):
    """Simple range attack"""
    action_name = 'range_attack'

    def __init__(self, game: 'GameInstance', action_data):
        if not isinstance(action_data['source'], BaseUnitObject):
            raise RuntimeError(f'This game object can not perform action {self.action_name}')
        super().__init__(game, action_data)

    @staticmethod
    def available_targets(game: 'GameInstance', unit: 'BaseUnitObject'):
        targets = game.get_hexes_in_range(unit.position, unit.attack_range + 1, allowed=[str(unit.priority_target)])
        return list(targets.values())

    def execute(self):
        if self.game.distance(self.source.position, self.target_hex) <= self.source.attack_range + 1:
            self.game.deal_damage(self.source, self.target_hex, self.source.damage)
            return {'action': self.action_name, 'target_hex': self.target_hex, 'damage': self.source.damage}
        raise RuntimeError('Cant attack target. Its too far')
    

class PathOfFire(SpellAction):
    """Path of fire spell"""
    action_name = 'path_of_fire'

    def __init__(self, game, action_request):
        super().__init__(game, action_request)
        if self.game.board.distance(self.game.hero.position, self.target_hex) > self.spell_effects['radius']:
            raise ActionNotAllowedError

    def execute(self):
        source = self.game.get_object_by_position(self.request.source)
        if self.game.distance(source.position, self.request.target_hex) <= source.spells:
            pass

        action_result = {}
        hero_hex = self.game.hero.position
        dq, dr = self.target_hex.q - hero_hex.q, self.target_hex.r - hero_hex.r
        target_hexes, target_units = [], []
        for i in range(1, int(self.spell_effects['path_length']) + 1):
            hex_id = f"{hero_hex.q + dq * i};{hero_hex.r + dr * i}"
            _hex = self.game.board[hex_id]
            # we build path of fire for path length or until meet an obstacle
            if not _hex or _hex.occupied_by == slotObstacle:
                break
            target_hexes.append(hex_id)
            if _hex.occupied_by == slotUnit:
                target_units.append(_hex)
        target_units = {_unit.pk: {} for _unit in self.game.units.values() if _unit.position in target_units}
        for _unit_id in target_units:
            target_units[_unit_id]['damage'] = self.game.damage_instance(self.game.hero, self.game.units[_unit_id],
                                                                         self.spell_effects['damage'])
        action_result['target_units'] = target_units
        action_result['target_hexes'] = target_hexes
        return action_result


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
        available_actions: Dict[str, List[str]] = {}
        for action in unit.actions:
            targets = cls._actions[action].available_targets(game, unit)
            if targets:
                available_actions[action] = targets
        return available_actions
