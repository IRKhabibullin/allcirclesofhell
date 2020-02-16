from unittest import TestCase
from random import random
from ..mechanics.board import Board, Hex
from ..mechanics.constants import slotEmpty, slotObstacle, slotUnit
from ..mechanics.game_objects import Obstacle


class BoardTestCase(TestCase):
    def setUp(self):
        self.board = Board(6)

    def test_created(self):
        hexes_count = 3 * self.board.radius ** 2 - 3 * self.board.radius + 1
        self.assertEqual(len(self.board.items()), hexes_count)

    def test_add(self):
        q, r = 2, 3
        self.board.get(f'{q};{r}').slot = Obstacle()
        test_hex = Hex(q, r, slotUnit)
        self.board.add(test_hex)
        self.assertEqual(self.board.get(f'{q};{r}').slot, slotUnit)

    def test_get_neighbors(self):
        if self.board.radius > 1:
            # test center hex, which should have 6 neighbors
            center_biases = [
                (1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)
            ]
            center_hex = self.board['0;0']
            neighbors = self.board.get_neighbors(center_hex)
            self.assertEqual(len(neighbors), 6)
            for _bias in center_biases:
                self.assertIn(self.board.get(f"{center_hex.q + _bias[0]};{center_hex.r + _bias[1]}"), neighbors)

            # test corner hex, which should have 3 neighbors
            corner_biases = [
                (1, -1), (0, -1), (-1, 0)
            ]
            corner_hex = self.board.get(f'0;{self.board.radius - 1}')
            neighbors = self.board.get_neighbors(corner_hex)
            self.assertEqual(len(neighbors), 3)
            for _bias in corner_biases:
                self.assertIn(self.board.get(f"{corner_hex.q + _bias[0]};{corner_hex.r + _bias[1]}"), neighbors)

            if self.board.radius > 2:
                # test side hex, which should have 4 neighbors
                side_biases = [
                    (1, 0), (1, -1), (-1, 1), (0, 1)
                ]
                side_hex = self.board.get(f'{-self.board.radius + 2};-1')
                neighbors = self.board.get_neighbors(side_hex)
                self.assertEqual(len(neighbors), 4)
                for _bias in side_biases:
                    self.assertIn(self.board.get(f"{side_hex.q + _bias[0]};{side_hex.r + _bias[1]}"), neighbors)

    def test_place_object(self):
        test_pk = 'test_pk'
        test_position = '3;-3'

        class GameObject:
            """Game object imitation for tests"""
            def __init__(self):
                self.pk = test_pk
                self.position = None

        test_object = GameObject()
        self.board.place_game_object(test_object, test_position)
        self.assertEqual(self.board[test_position].slot.pk, test_pk)

    def test_clear_board(self):

        class GameObject:
            """Game object imitation for tests"""
            def __init__(self):
                self.pk = 'test_pk'
                self.position = None

        test_hex = None
        while not test_hex:
            _coordinates = (int(random() * 2 * self.board.radius - self.board.radius),
                            int(random() * 2 * self.board.radius - self.board.radius))
            _coordinates = f'{_coordinates[0]};{_coordinates[1]}'
            if _coordinates in self.board and self.board[_coordinates].slot == slotEmpty:
                test_hex = self.board[_coordinates]

        self.board.place_game_object(GameObject(), test_hex.id)
        self.board.clear_board()
        self.assertIn(test_hex.slot, [slotEmpty])

    def test_get_hexes_in_range(self):
        hex_ranges = [
            # center
            {
                'hex': self.board.get('0;0'),
                'ranges': [(1, 7), (2, 19), (3, 37), (4, 61), (5, 91), (6, 91)]
            },
            # corner
            {
                'hex': self.board.get(f'0;{self.board.radius - 1}'),
                'ranges': [(1, 4), (2, 9), (3, 16), (4, 25), (5, 36), (6, 47), (7, 58), (8, 69), (9, 80), (10, 91),
                           (11, 91)]
            },
            # side
            {
                'hex': self.board.get(f'{-self.board.radius + 2};-1'),
                'ranges': [(1, 5), (2, 11), (3, 19), (4, 29), (5, 40), (6, 52), (7, 63), (8, 74), (9, 85), (10, 91),
                           (11, 91)]
            }
        ]

        for _data in hex_ranges:
            hexes_in_range = self.board.get_hexes_in_range(_data['hex'], 0)
            self.assertIn(f"{_data['hex'].q};{_data['hex'].r}", hexes_in_range)

            for _range in _data['ranges']:
                hexes_in_range = self.board.get_hexes_in_range(_data['hex'], _range[0])
                self.assertTrue(len(hexes_in_range), _range[1])

    def test_distance(self):
        hex_a = self.board.get('0;3')
        hex_b = self.board.get('1;-2')
        self.assertEqual(self.board.distance(hex_a, hex_b), 5)

    def test_get_state(self):
        state = self.board.get_state()
        self.assertEqual(state['radius'], self.board.radius)
        self.assertEqual(len(state['hexes']), len(self.board.items()))
