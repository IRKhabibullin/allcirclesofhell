import math
from random import shuffle

from game.mechanics import actions
from game.models import GameModel, Unit, Hero
from game.mechanics.board import Board


class GameInstance:
    """
    Class to manage single game instance
    """
    def __init__(self, game_model: GameModel = None):
        """
        Loading board from passed game model or generating new
        """
        if not game_model:
            self.game = GameModel()
        else:
            self.game = game_model

        if self.game.state != '{}':
            # from self.state
            pass
        else:
            self.board = Board(6)
        self.units = {}

    def init_round(self):
        """
        Initializing round
        Clearing the board
        Setting hero position
        Counting and placing units
        """
        self.units = {}
        self.board.clear_board()

        self.game.hero.position = f'0;{self.board.radius // 2}'
        hero_hex = self.board.hexes[self.game.hero.position]
        hero_hex['occupied_by'] = 'hero'
        self.game.hero.moves = list(
            self.board.get_hexes_in_range(hero_hex, self.game.hero.move_range, ['empty']).keys())
        self.game.hero.attack_hexes = list(
            self.board.get_hexes_in_range(hero_hex, self.game.hero.attack_range, ['empty', 'unit']).keys())
        max_unit_level = int(math.pow(2, math.floor(math.log2(self.game.round / 2)))) or 1
        available_hexes = {_id for _id, _hex in self.board.hexes.items() if _hex['occupied_by'] == 'empty'}
        clear_area_range = max(self.board.radius // 2 - self.game.round // 8, 1)
        hexes_in_range = self.board.get_hexes_in_range(self.board.hexes[self.game.hero.position],
                                                       clear_area_range, ['empty', 'hero'])
        available_hexes = list(available_hexes - hexes_in_range.keys())
        shuffle(available_hexes)

        def place_units(points: int, unit_level: int):
            """
            Counting units of current level and placing them on board.
            About half of remaining points goes to current level of units if its not 1 level unit
            Recursive call for units of lower level
            """
            u_count = points if unit_level == 1 else round((points // 2) / unit_level)
            for i in range(u_count):
                unit = Unit.objects.get(level=unit_level)
                unit.position = available_hexes.pop()
                unit.pk = len(self.units)
                _unit_hex = self.board.hexes[unit.position]
                _unit_hex['occupied_by'] = 'unit'
                self.units[unit.pk] = unit
            points_remain = int(points - u_count * unit_level)
            if points_remain:
                place_units(points_remain, unit_level // 2)

        place_units(self.game.round, max_unit_level)

        for unit in self.units.values():
            unit.moves = list(self.board.get_hexes_in_range(self.board.hexes[unit.position],
                                                            unit.move_range, ['empty']).keys())
            unit.attack_hexes = list(self.board.get_hexes_in_range(self.board.hexes[unit.position],
                                                                   unit.attack_range, ['empty', 'hero']).keys())

    def update_moves(self):
        hero_position = self.board.hexes.get(self.game.hero.position, None)
        self.game.hero.moves = list(
            self.board.get_hexes_in_range(hero_position, self.game.hero.move_range, ['empty']).keys())
        self.game.hero.attack_hexes = list(
            self.board.get_hexes_in_range(hero_position, self.game.hero.attack_range, ['empty', 'unit']).keys())
        for unit in self.units.values():
            _unit_hex = self.board.hexes[unit.position]
            unit.moves = list(self.board.get_hexes_in_range(_unit_hex, unit.move_range, ['empty']).keys())
            unit.attack_hexes = list(
                self.board.get_hexes_in_range(_unit_hex, unit.attack_range, ['empty', 'hero']).keys())

    def hero_action(self, action_data: dict) -> dict:
        """
        Make hero action
        """
        action_data['allowed'] = False
        if action_data['action'] in ['attack', 'range_attack']:
            action_data.update(getattr(actions, action_data['action'])(self, self.game.hero,
                                                                       self.units[action_data['target']]))
        else:
            action_data.update(getattr(actions, action_data['action'])(self, action_data))
        if not action_data['allowed']:
            return action_data
        # update hero's and units' possible moves
        action_data['units_actions'] = self.units_action(except_list=action_data.pop('stunned_units', []))
        self.update_moves()
        return action_data

    def units_action(self, except_list: list) -> list:
        """
        Units' actions. Follows after hero's action
        except_list: list of unit ids. These units doesnt act this time
        """
        units_actions = []
        for unit in self.units.values():
            if unit.pk in except_list:
                continue
            # try to find target to attack
            targets = [_hex for _hex in unit.attack_hexes if self.board.hexes[_hex]['occupied_by'] == 'hero']
            if targets:
                # suppose units can attack only hero for now
                attack_result = actions.attack(self, unit, self.game.hero)
                if attack_result['allowed']:
                    units_actions.append({'source': str(unit.pk), 'damage_dealt': attack_result['damage']})
            else:
                # try to move somewhere
                self.unit_move(unit)
        return units_actions

    def unit_move(self, unit: Unit):
        """
        Unit's move
        """
        _move_pos = None
        remaining_moves = set(unit.moves)
        while remaining_moves:
            _move_pos = remaining_moves.pop()
            if self.board.hexes[_move_pos]['occupied_by'] == 'empty':
                break
        if _move_pos:
            self.board.hexes[unit.position]['occupied_by'] = 'empty'
            unit.position = _move_pos
            self.board.place_game_object(unit)

    def damage_instance(self, source, target, damage):
        # apply damage modifiers
        # call pre-damage spells
        target.health -= damage
        # call after-damage spells
        if target.health <= 0:
            self.on_death(target)
        return damage

    def on_death(self, target):
        if isinstance(target, Hero):
            # game over
            pass
        elif isinstance(target, Unit):
            self.board.hexes[target.position]['occupied_by'] = 'empty'
            del self.units[target.pk]
