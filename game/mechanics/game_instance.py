import math
from random import shuffle, choice

from game.models import GameModel, Unit
from game.mechanics.board import Board


class GameInstance:
    def __init__(self, game_model=None):
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
        self.units = []
        self.board.clear_board()

        self.board.hexes[(0, self.board.radius // 2)]['occupied_by'] = 'hero'
        self.game.hero.position = (0, self.board.radius // 2)
        max_unit_level = int(math.pow(2, math.floor(math.log2(self.game.round / 2)))) or 1
        available_hexes = {_id for _id, _hex in self.board.hexes.items() if _hex['occupied_by'] == 'empty'}
        clear_area_range = max(self.board.radius // 2 - self.game.round // 8, 1)
        hexes_in_range = self.board.get_hexes_in_range(self.board.hexes[self.game.hero.position],
                                                       clear_area_range, ['empty', 'hero'])
        available_hexes = list(available_hexes - hexes_in_range.keys())
        shuffle(available_hexes)

        def place_units(points, unit_level):
            # about half of remaining points goes to current level of units if its not 1 level unit
            u_count = points if unit_level == 1 else round((points // 2) / unit_level)
            for i in range(u_count):
                _unit = Unit.objects.get(level=unit_level)
                _unit.position = available_hexes.pop()
                _unit.pk = len(self.units)
                self.board.place_game_object(_unit)
                _unit_hex = self.board.hexes[_unit.position]
                _unit.moves = list(self.board.get_hexes_in_range(_unit_hex, _unit.move_range).keys())
                _unit.attack_hexes = list(self.board.get_hexes_in_range(_unit_hex, _unit.attack_range).keys())
                self.units.append(_unit)
            points_remain = int(points - u_count * unit_level)
            if points_remain:
                place_units(points_remain, unit_level // 2)

        place_units(self.game.round, max_unit_level)

    def make_move(self, destination):
        hero_hex = self.board.hexes[self.game.hero.position]
        destination_hex = self.board.hexes.get(tuple(destination), hero_hex)
        if self.board.distance(destination_hex, hero_hex) != 1:
            print('move in place not allowed')
            return False
        if destination_hex['occupied_by'] != 'empty':
            print(f'move not allowed: place occupied by {destination_hex["occupied_by"]}')
            return False

        hero_hex['occupied_by'] = 'empty'
        self.game.hero.position = (destination_hex['q'], destination_hex['r'])
        destination_hex['occupied_by'] = 'hero'
        self.game.hero.moves = list(self.board.get_hexes_in_range(destination_hex, 1).keys())

        # first we move them all
        for _unit in self.units:
            if _unit.moves:
                _move_hex = None
                while not _move_hex:
                    _move_pos = choice(_unit.moves)
                    if self.board.hexes[_move_pos]['occupied_by'] == 'empty':
                        _move_hex = self.board.hexes[_move_pos]
                self.board.hexes[_unit.position]['occupied_by'] = 'empty'
                _unit.position = _move_pos
                self.board.place_game_object(_unit)

        # and then update their moves etc
        for _unit in self.units:
            _unit_hex = self.board.hexes[_unit.position]
            _unit.moves = list(self.board.get_hexes_in_range(_unit_hex, _unit.move_range).keys())
            _unit.attack_hexes = list(self.board.get_hexes_in_range(_unit_hex, _unit.attack_range).keys())
        print(f'move to {destination} allowed')
        return True
