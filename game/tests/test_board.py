from unittest import TestCase
from random import random
from ..mechanics.board import Board


class BoardTestCase(TestCase):
    def setUp(self):
        self.board = Board(6)

    def test_created(self):
        hexes_count = 3 * self.board.radius ** 2 - 3 * self.board.radius + 1
        self.assertEqual(len(self.board.hexes), hexes_count)

    def test_get_neighbors(self):
        if self.board.radius > 1:
            # test center hex, which should have 6 neighbors
            center_biases = [
                (1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)
            ]
            center_hex = self.board.hexes.get('0;0')
            neighbors = self.board.get_neighbors(center_hex)
            self.assertEqual(len(neighbors), 6)
            for _bias in center_biases:
                self.assertIn(self.board.hexes.get(f"{center_hex['q'] + _bias[0]};{center_hex['r'] + _bias[1]}", None),
                              neighbors)

            # test corner hex, which should have 3 neighbors
            corner_biases = [
                (1, -1), (0, -1), (-1, 0)
            ]
            corner_hex = self.board.hexes.get(f'0;{self.board.radius - 1}')
            neighbors = self.board.get_neighbors(corner_hex)
            self.assertEqual(len(neighbors), 3)
            for _bias in corner_biases:
                self.assertIn(self.board.hexes.get(f"{corner_hex['q'] + _bias[0]};{corner_hex['r'] + _bias[1]}", None),
                              neighbors)

            if self.board.radius > 2:
                # test side hex, which should have 4 neighbors
                side_biases = [
                    (1, 0), (1, -1), (-1, 1), (0, 1)
                ]
                side_hex = self.board.hexes.get(f'{-self.board.radius + 2};-1')
                neighbors = self.board.get_neighbors(side_hex)
                self.assertEqual(len(neighbors), 4)
                for _bias in side_biases:
                    self.assertIn(self.board.hexes.get(f"{side_hex['q'] + _bias[0]};{side_hex['r'] + _bias[1]}", None),
                                  neighbors)

    def test_clear_board(self):
        test_hex = None
        while not test_hex:
            _coords = (int(random() * 2 * self.board.radius - self.board.radius),
                       int(random() * 2 * self.board.radius - self.board.radius))
            _coords = f'{_coords[0]};{_coords[1]}'
            if _coords in self.board.hexes and self.board.hexes[_coords]['occupied_by'] == 'empty':
                test_hex = self.board.hexes[_coords]
        test_hex['occupied_by'] = 'testing value'
        self.board.clear_board()
        self.assertIn(test_hex['occupied_by'], ['empty', 'obstacle'])

    def test_place_object(self):
        class GameObject:
            def __init__(self, pk, position):
                self.pk = pk
                self.position = position

        test_pk, test_position = 'test_pk', '3;-3'
        test_object = GameObject(test_pk, test_position)
        self.board.place_game_object(test_object)
        self.assertEqual(self.board.hexes[test_position]['occupied_by'], test_pk)

    def test_get_hexes_in_range(self):
        hex_ranges = [
            # center
            {
                'hex': self.board.hexes.get('0;0'),
                'ranges': [(1, 7), (2, 19), (3, 37), (4, 61), (5, 91), (6, 91)]
            },
            # corner
            {
                'hex': self.board.hexes.get(f'0;{self.board.radius - 1}'),
                'ranges': [(1, 4), (2, 9), (3, 16), (4, 25), (5, 36), (6, 47), (7, 58), (8, 69), (9, 80), (10, 91),
                           (11, 91)]
            },
            # side
            {
                'hex': self.board.hexes.get(f'{-self.board.radius + 2};-1'),
                'ranges': [(1, 5), (2, 11), (3, 19), (4, 29), (5, 40), (6, 52), (7, 63), (8, 74), (9, 85), (10, 91),
                           (11, 91)]
            }
        ]

        for _data in hex_ranges:
            hexes_in_range = self.board.get_hexes_in_range(_data['hex'], 0)
            self.assertIn(f"{_data['hex']['q']};{_data['hex']['r']}", hexes_in_range)

            for _range in _data['ranges']:
                hexes_in_range = self.board.get_hexes_in_range(_data['hex'], _range[0])
                self.assertTrue(len(hexes_in_range), _range[1])
