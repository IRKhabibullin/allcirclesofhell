from random import random

# chances in percents
OBSTACLE_CHANCE = 15


class Board:
    position_biases = [
        (1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)
    ]

    def __init__(self, radius: int):
        self.radius = radius
        self.hexes = {}

        def create_neighbors(_hex: Hex):
            for bias in self.position_biases:
                new_pos = tuple(sum(x) for x in zip((_hex['q'], _hex['r']), bias))
                if new_pos in self.hexes:
                    continue
                if abs(new_pos[0] + new_pos[1]) >= self.radius:
                    continue
                if any(pos in [self.radius, -self.radius] for pos in new_pos):
                    continue
                new_hex = Hex(*new_pos)
                self.hexes[new_pos] = new_hex
                create_neighbors(new_hex)

        # todo write algorithms for obstacles generating
        start_hex = Hex(0, 0)
        self.hexes[(0, 0)] = start_hex
        create_neighbors(start_hex)

    def get_neighbors(self, _hex):
        _neighbors = []
        for bias in self.position_biases:
            _neighbor = self.hexes.get(tuple(sum(x) for x in zip((_hex['q'], _hex['r']), bias)), None)
            if _neighbor:
                _neighbors.append(_neighbor)
        return _neighbors

    def get_hexes_in_range(self, center_hex: dict, _range: int, occupied_by=None) -> dict:
        hexes_in_range = {}
        for q in range(-_range, _range + 1):
            for r in range(max(-_range, -q - _range),
                           min(_range, -q + _range) + 1):
                _q, _r = q + center_hex['q'], r + center_hex['r']
                if (_q, _r) in self.hexes:
                    _hex = self.hexes[(_q, _r)]
                    if not occupied_by or _hex['occupied_by'] in occupied_by:
                        hexes_in_range[(_q, _r)] = _hex
        return hexes_in_range

    def place_game_object(self, game_object):
        # maybe need to check for occupied. And add param 'forced_placing'
        self.hexes[game_object.position]['occupied_by'] = game_object.pk

    def clear_board(self):
        for _hex in self.hexes.values():
            _hex['occupied_by'] = 'empty'
            if int(random() * 100) < OBSTACLE_CHANCE:
                _hex['occupied_by'] = 'obstacle'

    @staticmethod
    def distance(hex_a, hex_b):
        return max(abs(hex_a['x'] - hex_b['x']), abs(hex_a['y'] - hex_b['y']), abs(hex_a['z'] - hex_b['z']))

    def get_state(self):
        return {'radius': self.radius,
                'hexes': list(self.hexes.values())
                }


def Hex(q: int, r: int, occupied_by: str = 'empty'):
    return {
        'q': q,
        'r': r,
        'x': q,
        'y': -q - r,
        'z': r,
        'occupied_by': occupied_by
    }


