from unittest import TestCase
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
            center_hex = self.board.hexes.get((0, 0))
            neighbors = self.board.get_neighbors(center_hex)
            self.assertEqual(len(neighbors), 6)
            for _bias in center_biases:
                self.assertIn(self.board.hexes.get((center_hex['x'] + _bias[0], center_hex['y'] + _bias[1]), None),
                              neighbors)

            # test corner hex, which should have 3 neighbors
            corner_biases = [
                (1, -1), (0, -1), (-1, 0)
            ]
            corner_hex = self.board.hexes.get((0, self.board.radius - 1))
            neighbors = self.board.get_neighbors(corner_hex)
            self.assertEqual(len(neighbors), 3)
            for _bias in corner_biases:
                self.assertIn(self.board.hexes.get((corner_hex['x'] + _bias[0], corner_hex['y'] + _bias[1]), None),
                              neighbors)

            if self.board.radius > 2:
                # test side hex, which should have 4 neighbors
                side_biases = [
                    (1, 0), (1, -1), (-1, 1), (0, 1)
                ]
                side_hex = self.board.hexes.get((-self.board.radius + 2, -1))
                neighbors = self.board.get_neighbors(side_hex)
                self.assertEqual(len(neighbors), 4)
                for _bias in side_biases:
                    self.assertIn(self.board.hexes.get((side_hex['x'] + _bias[0], side_hex['y'] + _bias[1]), None),
                                  neighbors)


