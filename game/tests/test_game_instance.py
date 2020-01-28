"""Tests for game instance"""

from django.test import TestCase

from game.mechanics.constants import ocpUnit
from game.mechanics.game_instance import GameInstance
from game.models import Hero, GameModel


class GameInstanceTestCase(TestCase):
    fixtures = ['test_fixture.json']

    def setUp(self):
        game_model = GameModel.objects.get(pk=1)
        self.game = GameInstance(game_model)

    def test_game_loaded(self):
        self.assertEqual(self.game.hero.name, 'Genos')

    def test_init_round(self):
        self.game.init_round()
        self.assertEqual(self.game.hero.position.id, '0;3')
        self.assertDictEqual(self.game.board.get_hexes_in_range(self.game.hero.position, 3, [ocpUnit]), {})
        self.assertEqual(sum([unit.level for unit in self.game.units.values()]), self.game._game.round)
