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
    """Results of game turn"""
    def __init__(self, name: str):
        self.name: str = name
        self.state: str = 'success'
        # actions made by units
        self.hero_actions: Dict[str: list] = {}
        self.units_actions: Dict[Dict[str: list]] = defaultdict(dict)

    def to_dict(self):
        """Serialize response to pass to ui"""
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
        """Find possible targets for this action for given unit"""
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
        if self.game.distance(self.source.position, self.target_hex) > self.source.move_range:
            raise RuntimeError('Cant move there')
        self.game.move_object(self.source, self.target_hex)
        return {self.action_name: [{'target_hex': self.target_hex}]}


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
            spell = unit.spells.get(code_name=cls.action_name)
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
            hex_slot = self.game.get_object_by_position(hex_id)
            if not hex_slot or str(hex_slot) == slotObstacle:
                break
            self.game.deal_damage(hex_id, self.spell_effects['damage'])
            action_steps.append({'target_hex': hex_id, 'damage': self.spell_effects['damage']})
        return {self.action_name: action_steps}


class ShieldBash(SpellAction):
    """Shield bash spell"""
    action_name = 'shield_bash'

    def __init__(self, game, action_data):
        super().__init__(game, action_data)

    @classmethod
    def available_targets(cls, game: 'GameInstance', unit: 'BaseUnitObject') -> 'List[Hex]':
        try:
            spell = unit.spells.get(code_name=cls.action_name)
        except SpellModel.DoesNotExist:
            raise RuntimeError('Action not allowed')
        spell_effects = {item.effect.code_name: item.value for item in spell.spelleffectmodel_set.all()}
        targets = game.get_hexes_in_range(unit.position, spell_effects['radius']).values()
        targets = [_hex for _hex in targets if unit.position != _hex]
        return targets

    def execute(self) -> Dict[str, List]:
        if self.game.distance(self.source.position, self.target_hex) > self.spell_effects['radius']:
            raise RuntimeError('Target is too far')

        action_steps = []
        # find hexes affected by spell (target itself and two neighbours
        source_area = self.game.get_hexes_in_range(self.source.position,
                                                   self.game.distance(self.source.position, self.target_hex))
        affected_hexes = {hex_id: source_area[hex_id] for hex_id in set(source_area).intersection(
            self.game.get_hexes_in_range(self.game.board.get(self.target_hex), 1))}
        # define hex where bash comes from. For spell range 1 its hero himself
        distances = {hex_id: self.game.distance(self.source.position, hex_id) for hex_id in affected_hexes}
        bash_source = affected_hexes.pop(min(distances, key=distances.get))

        for hex_id in affected_hexes:
            hex_slot = self.game.get_object_by_position(hex_id)
            action_step = {'target_hex': hex_id}
            if isinstance(hex_slot, BaseUnitObject):
                dq = source_area[hex_id].q - bash_source.q
                dr = source_area[hex_id].r - bash_source.r
                hex_behind = f"{source_area[hex_id].q + dq};{source_area[hex_id].r + dr}"
                if not self.game.board.get(hex_behind) or self.game.get_object_by_position(hex_behind) != slotEmpty:
                    action_step['damage'] = self.spell_effects['damage'] * 2
                else:
                    action_step['damage'] = self.spell_effects['damage']
                    self.game.move_object(hex_slot, hex_behind)
                    action_step['pushed_to'] = hex_behind
                self.game.deal_damage(hex_id, action_step['damage'])
            if hex_id == self.target_hex:
                action_step['main_target'] = True
            if len(action_step) > 1:
                action_steps.append(action_step)
        # todo stun these units, so they won't act. Maybe add int field 'stunned' to units and countdown it each turn
        return {self.action_name: action_steps}


class Blink(SpellAction):
    """Blink spell"""
    action_name = 'blink'

    def __init__(self, game: 'GameInstance', action_data):
        if not isinstance(action_data['source'], BaseUnitObject):
            raise RuntimeError(f'This game object can not perform action {self.action_name}')
        super().__init__(game, action_data)

    @classmethod
    def available_targets(cls, game: 'GameInstance', unit: 'BaseUnitObject'):
        try:
            spell = unit.spells.get(code_name=cls.action_name)
        except SpellModel.DoesNotExist:
            raise RuntimeError('Action not allowed')
        spell_effects = {item.effect.code_name: item.value for item in spell.spelleffectmodel_set.all()}
        targets = game.get_hexes_in_range(unit.position, spell_effects['radius'], allowed=[slotEmpty])
        return list(targets.values())

    def execute(self) -> Dict[str, List]:
        if self.game.distance(self.source.position, self.target_hex) > self.spell_effects['radius']:
            raise RuntimeError('Cant move there')
        self.game.move_object(self.source, self.target_hex)
        return {self.action_name: [{'target_hex': self.target_hex}]}


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

    @classmethod
    def get_action(cls, game: 'GameInstance', action_data: dict) -> Action:
        """Create action instance from given data"""
        if action_data['action'] in cls._actions:
            action = cls._actions[action_data['action']](game, action_data)
            return action
        raise RuntimeError('No such action')

    @classmethod
    def available_actions(cls, game: 'GameInstance', unit: 'BaseUnitObject') -> 'Dict[str, List[Hex]]':
        """Find available actions for given unit and possible targets for them"""
        available_actions: Dict[str, List[Hex]] = {}
        for action in unit.actions:
            targets = cls._actions[action].available_targets(game, unit)
            if targets:
                available_actions[action] = targets
        return available_actions
