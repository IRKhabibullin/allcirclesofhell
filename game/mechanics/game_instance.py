import math
from random import shuffle

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

        max_unit_level = int(math.pow(2, math.floor(math.log2(self.game.round / 2)))) or 1
        available_hexes = {_id for _id, _hex in self.board.hexes.items() if _hex['occupied_by'] == 'empty'}
        clear_area_range = max(self.board.radius // 2 - self.game.round // 8, 1)
        hexes_in_range = self.board.get_hexes_in_range(self.board.hero_hex, clear_area_range)
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
                # self.units[_unit.pk] = _unit
                self.units.append(_unit)
            points_remain = int(points - u_count * unit_level)
            if points_remain:
                place_units(points_remain, unit_level // 2)

        place_units(self.game.round, max_unit_level)
