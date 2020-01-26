"""Tests for game instance"""

from django.test import TestCase
from game.mechanics.game_instance import GameInstance
from game.models import Hero, GameModel


class GameInstanceTestCase(TestCase):
    fixtures = ['test_fixture.json']

    def setUp(self):
        game_model = GameModel.objects.first()
        self.game = GameInstance(game_model)

    def test_game_loaded(self):
        self.assertEqual(self.game.hero.name, 'Genos')
