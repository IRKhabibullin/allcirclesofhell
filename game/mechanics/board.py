from random import random

# chances in percents
OBSTACLE_CHANCE = 15


class Board:
    def __init__(self, height: int, width: int):
        self.height = height
        self.width = width
        self.hexes = []

        # todo write algorithms for obstacles generating
        hero_tile = [self.width // 2, self.height - 2]
        for r in range(height):
            for c in range(width):
                extras = {}
                if [c, r] == hero_tile:
                    extras['_type'] = 'hero_tile'
                elif int(random() * 100) < OBSTACLE_CHANCE:
                    extras['_type'] = 'obstacle'
                self.hexes.append(Hex(c, r, **extras))

    def get_state(self):
        return {'height': self.height,
                'width': self.width,
                'hexes': [{'c': _h['c'], 'r': _h['r'], 'type': _h['type']} for _h in self.hexes]
                }


def Hex(c: int, r: int, _type: str = 'empty'):
    z = r - (c - (c & 1)) / 2
    return {
        'c': c,
        'r': r,
        'x': c,
        'z': z,
        'y': -c - z,
        'type': _type
    }


