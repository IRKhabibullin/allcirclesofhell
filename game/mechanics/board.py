from random import random
from game.models import Unit

# chances in percents
OBSTACLE_CHANCE = 15


class Board:
    """
    Game board, made of hexes, positioned in hexagonal form
    """
    position_biases = [
        (1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)
    ]

    def __init__(self, radius: int):
        self.radius = radius
        self.hexes = {}

        def create_neighbors(_hex: 'Hex'):
            """
            Method generating grid of hexes in board
            """
            for bias in self.position_biases:
                new_pos = [sum(x) for x in zip((_hex['q'], _hex['r']), bias)]
                new_id = f'{new_pos[0]};{new_pos[1]}'
                if new_id in self.hexes:
                    continue
                if abs(new_pos[0] + new_pos[1]) >= self.radius:
                    continue
                if any(pos in [self.radius, -self.radius] for pos in new_pos):
                    continue
                new_hex = Hex(*new_pos)
                self.hexes[new_id] = new_hex
                create_neighbors(new_hex)

        # todo write algorithms for obstacles generating
        start_hex = Hex(0, 0)
        self.hexes['0;0'] = start_hex
        create_neighbors(start_hex)

    def get_neighbors(self, _hex: 'Hex') -> list:
        """
        Get neighboring hexes.
        Up to 6 neighbors for given hex (Could be on the edge of board and will have less neighbors)
        """
        _neighbors = []
        for bias in self.position_biases:
            _neighbor = self.hexes.get(f"{_hex['q'] + bias[0]};{_hex['r'] + bias[1]}", None)
            if _neighbor:
                _neighbors.append(_neighbor)
        return _neighbors

    def get_hexes_in_range(self, center_hex: dict, _range: int, occupied_by: list = None) -> dict:
        """
        Get hexes in <_range> away from <center_hex>. Center hex itself counts for range 1
        Can specify allowed hex occupation.
        Hexes, occupied by object of type that NOT in <occupied_by>, not included in result
        """
        hexes_in_range = {}
        for q in range(-_range, _range + 1):
            for r in range(max(-_range, -q - _range),
                           min(_range, -q + _range) + 1):
                _hex_id = f"{q + center_hex['q']};{r + center_hex['r']}"
                if _hex_id in self.hexes:
                    _hex = self.hexes[_hex_id]
                    if not occupied_by or _hex['occupied_by'] in occupied_by:
                        hexes_in_range[_hex_id] = _hex
        return hexes_in_range

    def place_game_object(self, game_object):
        """
        Place game object in board according to it's position.
        Game object must have <position> and <pk> attributes. Usually its django models
        """
        # maybe need to check for occupied. And add param 'forced_placing'
        if isinstance(game_object, Unit):
            self.hexes[game_object.position]['occupied_by'] = 'unit'
            return
        self.hexes[game_object.position]['occupied_by'] = game_object.pk

    def clear_board(self):
        """
        Clear board from units, hero, game objects. Re-generate obstacles
        """
        # todo move obstacles generating into function and call it separately
        for _hex in self.hexes.values():
            _hex['occupied_by'] = 'empty'
            if int(random() * 100) < OBSTACLE_CHANCE:
                _hex['occupied_by'] = 'obstacle'

    @staticmethod
    def distance(hex_a, hex_b):
        """
        Get distance between two hexes
        """
        return max(abs(hex_a['x'] - hex_b['x']), abs(hex_a['y'] - hex_b['y']), abs(hex_a['z'] - hex_b['z']))

    def get_state(self):
        """
        Get serialized board state
        """
        return {'radius': self.radius, 'hexes': self.hexes}


def Hex(q: int, r: int, occupied_by: str = 'empty') -> dict:
    """
    Hex object, used in board
    """
    return {
        'q': q,
        'r': r,
        'x': q,
        'y': -q - r,
        'z': r,
        'occupied_by': occupied_by
    }


