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

        def create_neighbors(hex: Hex):
            for bias in self.position_biases:
                new_pos = tuple(sum(x) for x in zip((hex['x'], hex['y']), bias))
                if new_pos in self.hexes:
                    continue
                if abs(new_pos[0] + new_pos[1]) >= self.radius:
                    continue
                if any(pos in [self.radius, -self.radius] for pos in new_pos):
                    continue
                extras = {}
                if [new_pos[0], new_pos[1]] == hero_tile:
                    extras['_type'] = 'hero_tile'
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

        # for r in range(height):
        #     for c in range(width):
        #         extras = {}
        #         if [c, r] == hero_tile:
        #             extras['_type'] = 'hero_tile'
        #         elif int(random() * 100) < OBSTACLE_CHANCE:
        #             extras['_type'] = 'obstacle'
        #         self.hexes.append(Hex(c, r, **extras))

    def get_state(self):
        self.hexes[(-2, 2)]['r'] = -1
        self.hexes[(2, -2)]['r'] = 1
        self.hexes[(-1, 2)]['r'] = -2
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
        'type': _type
    }


