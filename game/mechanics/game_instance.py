import math
from random import shuffle

from game.models import GameModel, Unit
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
        self.units = []

    def init_round(self):
        """
        Initializing round
        Clearing the board
        Setting hero position
        Counting and placing units
        """
        self.units = []
        self.board.clear_board()

        self.game.hero.position = (0, self.board.radius // 2)
        hero_hex = self.board.hexes[self.game.hero.position]
        hero_hex['occupied_by'] = 'hero'
        self.game.hero.moves = list(self.board.get_hexes_in_range(hero_hex, 1, ['empty']).keys())
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
                self.board.place_game_object(unit)
                _unit_hex = self.board.hexes[unit.position]
                unit.moves = list(self.board.get_hexes_in_range(_unit_hex, unit.move_range, ['empty']).keys())
                unit.attack_hexes = list(self.board.get_hexes_in_range(_unit_hex, unit.attack_range, ['empty']).keys())
                self.units.append(unit)
            points_remain = int(points - u_count * unit_level)
            if points_remain:
                place_units(points_remain, unit_level // 2)

        place_units(self.game.round, max_unit_level)

    def hero_action(self, action_data: dict) -> bool:
        """
        Make hero action
        """
        if action_data['action'] == 'move':
            destination = self.board.hexes.get(tuple(action_data['destination']), None)
            if not destination:
                return False
            result = self.hero_move(destination)
            if not result:
                return result
            self.units_action()

            # update hero's and units' possible moves
            self.game.hero.moves = list(self.board.get_hexes_in_range(destination, 1, ['empty']).keys())
            for unit in self.units:
                _unit_hex = self.board.hexes[unit.position]
                unit.moves = list(self.board.get_hexes_in_range(_unit_hex, unit.move_range, ['empty']).keys())
                unit.attack_hexes = list(self.board.get_hexes_in_range(_unit_hex, unit.attack_range, ['empty']).keys())
            return result

    def hero_move(self, destination: 'Hex') -> bool:
        """
        Make hero move
        """
        hero_hex = self.board.hexes[self.game.hero.position]
        if self.board.distance(destination, hero_hex) != 1:
            print('move in place not allowed')
            return False
        if destination['occupied_by'] != 'empty':
            print(f'move not allowed: place occupied by {destination["occupied_by"]}')
            return False

        hero_hex['occupied_by'] = 'empty'
        self.game.hero.position = (destination['q'], destination['r'])
        destination['occupied_by'] = 'hero'
        print(f'move to {destination} allowed')
        return True

    def units_action(self):
        """
        Units' actions. Follows after hero's action
        """
        for unit in self.units:
            self.unit_move(unit)

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
