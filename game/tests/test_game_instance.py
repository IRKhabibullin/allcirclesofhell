"""Tests for game instance"""
from unittest import TestCase

from django.contrib.auth.models import User
from django.test import TestCase

from game.mechanics.constants import slotUnit
from game.mechanics.game_instance import GameInstance
from game.models import HeroModel, GameModel


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
        self.assertDictEqual(self.game.board.get_hexes_in_range(self.game.hero.position, 3, allowed=[slotUnit]), {})
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

    def find_movable_unit(self):
        unit = None
        # we will try to find movable unit 5 times. else raise exception
        for i in range(5):
            self.game.init_round()
            for _unit in self.game.units.values():
                if _unit.moves:
                    return _unit
        raise AssertionError

    def test_unit_move(self):
        unit = self.find_movable_unit()
        unit_moves = unit.moves
        self.game.unit_move(unit)
        # check that after move unit stays at one of previously available hexes
        self.assertIn(unit.position.id, unit_moves)

        unit.moves = []
        unit_position = unit.position
        self.game.unit_move(unit)
        # when no moves check that unit stays in place
        self.assertEqual(unit.position, unit_position)
