from random import random


class Battlefield:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.hexes = []

        #  chances in percents
        obstacle_chance = 7
        for r in range(rows):
            for c in range(cols):
                extras = {}
                if int(random() * obstacle_chance):
                    extras['_type'] = 'obstacle'
                self.hexes.append(Hex(c, r, **extras))


def Hex(c, r, _type='empty'):
    z = r - (c - (c & 1)) / 2
    return {
        'c': c,
        'r': r,
        'x': c,
        'z': z,
        'y': -c - z,
        'type': _type
    }


