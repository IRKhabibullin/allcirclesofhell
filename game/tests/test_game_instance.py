"""Tests for game instance"""

from django.contrib.auth.models import User
from django.test import TestCase

from game.mechanics.constants import slotUnit
from game.mechanics.game_instance import GameInstance
from game.models import GameModel


class GameInstanceTestCase(TestCase):
    fixtures = ['test_fixture.json']

    def setUp(self):
        game_model = GameModel.objects.get(pk=1)
        self.game = GameInstance(game_model)

    def test_game_loaded(self):
        self.assertEqual(self.game.hero.name, 'Genos')

    def test_init_round(self):
        self.game.start_round()
        self.assertEqual(self.game.hero.position.id, '0;3')
        self.assertDictEqual(self.game._board.get_hexes_in_range(self.game.hero.position, 3, allowed=[slotUnit]), {})
        self.assertEqual(sum([unit.level for unit in self.game.units.values()]), self.game._game.round)

    def test_new(self):
        user = User.objects.get(pk=2)
        hero_dict = {'name': 'Okomoto'}
        game_id, game_instance = GameInstance.new(user, hero_dict)
        self.assertEqual(game_instance._game.user, user)
        self.assertEqual(game_instance.hero.name, hero_dict['name'])

    def test_load(self):
        user = User.objects.get(pk=2)
        game_instance = GameInstance.load(1)
        self.assertEqual(game_instance._game.user, user)
        self.assertEqual(game_instance.hero.name, 'Genos')
