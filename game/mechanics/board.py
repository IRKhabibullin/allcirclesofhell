from random import random

# chances in percents
OBSTACLE_CHANCE = 15


class Board:
    position_biases = [
        [1, 0], [1, -1], [0, -1], [-1, 0], [-1, 1], [0, 1]
    ]

    def __init__(self, radius: int):
        self.radius = radius
        self.hexes = {}

        def create_neighbors(_hex: Hex):
            for bias in self.position_biases:
                new_pos = tuple(sum(x) for x in zip((_hex['x'], _hex['y']), bias))
                if new_pos in self.hexes:
                    continue
                if abs(new_pos[0] + new_pos[1]) >= self.radius:
                    continue
                if any(pos in [self.radius, -self.radius] for pos in new_pos):
                    continue
                extras = {}
                if [new_pos[0], new_pos[1]] == hero_tile:
                    extras['_type'] = 'hero'
                elif int(random() * 100) < OBSTACLE_CHANCE:
                    extras['_type'] = 'obstacle'
                new_hex = Hex(*new_pos, **extras)
                self.hexes[new_pos] = new_hex
                create_neighbors(new_hex)

        # todo write algorithms for obstacles generating
        hero_tile = [0, self.radius - 2]
        start_hex = Hex(0, 0)
        self.hexes[(0, 0)] = start_hex
        create_neighbors(start_hex)

    def getNeighbors(self, _hex):
        _neighbors = []
        for bias in self.position_biases:
            _neighbor = self.hexes.get(tuple(sum(x) for x in zip((_hex['x'], _hex['y']), bias)), None)
            if _neighbor:
                _neighbors.append(_neighbor)
        return _neighbors

    def get_state(self):
        return {'radius': self.radius,
                'hexes': list(self.hexes.values())
                }


def Hex(x: int, y: int, _type: str = 'empty'):
    s = y - (x - (x & 1)) / 2
    return {
        'x': x,
        'y': y,
        'q': x,
        's': s,
        'r': -x - s,
        'tile_type': _type
    }


