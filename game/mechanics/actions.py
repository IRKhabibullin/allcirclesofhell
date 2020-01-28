"""
Functions for actions
"""
from game.models import Spell
from game.mechanics.constants import ocpEmpty, ocpObstacle, ocpUnit


class ActionNotAllowedError(Exception):
    """Exception raised when action could not be executed"""
    pass


class Action:
    """Base class for all game actions"""
    action_name: str

    def __init__(self, game, action_data):
        self.game = game
        self.target_hex = self.game.board.get(action_data.get('target_hex', None))
        self.target_unit = self.game.units.get(action_data.get('target_unit', None), None)
        if not self.target_hex and not self.target_unit:
            raise ActionNotAllowedError

    def execute(self):
        """Main method to execute action"""
        raise NotImplementedError


class SpellAction(Action):
    """Base class for all spell actions"""
    action_name: str

    def __init__(self, game, action_data):
        super().__init__(game, action_data)
        try:
            self.spell = self.game.hero.spells.get(code_name=self.action_name)
        except Spell.DoesNotExist:
            raise ActionNotAllowedError
        self.spell_effects = {item.effect.code_name: item.value for item in self.spell.spelleffect_set.all()}


class Move(Action):
    """Simple move"""
    action_name = 'move'

    def __init__(self, game, action_data):
        super().__init__(game, action_data)
        if self.target_hex.occupied_by != ocpEmpty:
            raise ActionNotAllowedError
        if self.game.board.distance(self.target_hex, self.game.hero.position) > self.game.hero.move_range:
            raise ActionNotAllowedError

    def execute(self):
        self.game.board.place_game_object(self.game.hero, self.target_hex.id)
        return {}


class Attack(Action):
    """Simple attack"""
    action_name = 'attack'

    def __init__(self, game, action_data):
        super().__init__(game, action_data)
        if action_data.get('hero_attack', True):
            self.attacker = self.game.hero
        else:
            self.attacker = self.target_unit
            self.target_unit = self.game.hero
        if self.game.board.distance(self.attacker.position, self.target_unit.position) > self.attacker.attack_range:
            raise ActionNotAllowedError

    def execute(self):
        damage_dealt = self.game.damage_instance(self.attacker, self.target_unit, self.attacker.damage)
        return {'target': self.target_unit.pk, 'damage': damage_dealt}


class RangeAttack(Action):
    """Simple range attack"""
    action_name = 'attack'

    def __init__(self, game, action_data):
        super().__init__(game, action_data)
        if self.game.board.distance(self.game.hero.position,
                                    self.target_unit.position) > self.game.hero.attack_range + 1:
            raise ActionNotAllowedError

    def execute(self):
        damage_dealt = self.game.damage_instance(self.game.hero, self.target_unit, self.game.hero.damage)
        return {'target': self.target_unit.pk, 'damage': damage_dealt}


class PathOfFire(SpellAction):
    """Path of fire spell"""
    action_name = 'path_of_fire'

    def __init__(self, game, action_data):
        super().__init__(game, action_data)
        if self.game.board.distance(self.game.hero.position, self.target_hex) > self.spell_effects['radius']:
            raise ActionNotAllowedError

    def execute(self):
        action_result = {}
        hero_hex = self.game.hero.position
        dq, dr = self.target_hex.q - hero_hex.q, self.target_hex.r - hero_hex.r
        target_hexes, target_units = [], []
        for i in range(1, int(self.spell_effects['path_length']) + 1):
            hex_id = f"{hero_hex.q + dq * i};{hero_hex.r + dr * i}"
            _hex = self.game.board[hex_id]
            # we build path of fire for path length or until meet an obstacle
            if not _hex or _hex.occupied_by == ocpObstacle:
                break
            target_hexes.append(hex_id)
            if _hex.occupied_by == ocpUnit:
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

    def __init__(self, game, action_data):
        super().__init__(game, action_data)
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
            if not hex_behind or hex_behind.occupied_by != ocpEmpty:
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

    def __init__(self, game, action_data):
        super().__init__(game, action_data)
        if self.target_hex.occupied_by != ocpEmpty:
            raise ActionNotAllowedError
        if self.game.board.distance(self.game.hero.position, self.target_hex) > self.spell_effects['radius']:
            raise ActionNotAllowedError

    def execute(self):
        self.game.board.place_game_object(self.game.hero, self.target_hex.id)
        return {}


class ActionManager:
    """Class to manage all actions"""
    _actions_mapping = {
        'move': Move,
        'attack': Attack,
        'range_attack': RangeAttack,
        'path_of_fire': PathOfFire,
        'shield_bash': ShieldBash,
        'blink': Blink,
    }

    @staticmethod
    def execute(game, action_data):
        """Executes action and returns results"""
        return {'allowed': True, **ActionManager._actions_mapping[action_data['action']](game, action_data).execute()}
