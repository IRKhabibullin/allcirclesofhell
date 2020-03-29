from django.test import TestCase

from ..mechanics.actions import Idle, Move, Attack, RangeAttack, PathOfFire, ShieldBash, Blink
from ..mechanics.game_instance import GameInstance
from ..mechanics.game_objects import Hero
from ..models import GameModel


class ActionsTestCase(TestCase):
    fixtures = ['test_fixture.json']

    def setUp(self):
        game_model = GameModel.objects.get(pk=2)
        self.game = GameInstance(game_model)

    def test_idle(self):
        self.game.load_state()
        action = Idle(self.game, {'source': self.game.hero})
        self.assertEqual(action.execute(), {})

    def test_move(self):
        self.game.load_state()
        action = Move(self.game, {'source': self.game.hero, 'target_hex': '1;2'})
        self.assertEqual(action.execute(), {'move': [{'target_hex': '1;2'}]})
        new_position = self.game.get_hex('1;2')
        self.assertEqual(self.game.hero.position, new_position)
        self.assertEqual(new_position.slot, self.game.hero)

    def test_move_failed(self):
        self.game.load_state()
        # moving into obstacle
        action = Move(self.game, {'source': self.game.hero, 'target_hex': '1;3'})
        self.assertRaises(RuntimeError, action.execute)
        # moving into unit
        action = Move(self.game, {'source': self.game.hero, 'target_hex': '-1;4'})
        self.assertRaises(RuntimeError, action.execute)
        # moving too far
        action = Move(self.game, {'source': self.game.hero, 'target_hex': '2;1'})
        self.assertRaises(RuntimeError, action.execute)

    def test_attack(self):
        self.game.load_state()
        # hit unit
        action = Attack(self.game, {'source': self.game.hero, 'target_hex': '-1;4'})
        self.assertEqual(action.execute(), {'attack': [{'target_hex': '-1;4', 'damage': 5}]})
        # hit empty hex. Info about target is passed to ui for animation, but no info about damage dealt
        self.game.load_state()
        action = Attack(self.game, {'source': self.game.hero, 'target_hex': '-1;3'})
        self.assertEqual(action.execute(), {'attack': [{'target_hex': '-1;3'}]})
        # hit obstacle
        self.game.load_state()
        action = Attack(self.game, {'source': self.game.hero, 'target_hex': '1;3'})
        self.assertEqual(action.execute(), {'attack': [{'target_hex': '1;3'}]})

    def test_attack_failed(self):
        self.game.load_state()
        # hit unit out of distance
        action = Attack(self.game, {'source': self.game.hero, 'target_hex': '0;1'})
        self.assertRaises(RuntimeError, action.execute)

    def test_range_attack(self):
        self.game.load_state()
        # hit unit in range 1
        action = RangeAttack(self.game, {'source': self.game.hero, 'target_hex': '-1;4'})
        self.assertEqual(action.execute(), {'range_attack': [{'target_hex': '-1;4', 'damage': 5}]})
        # hit unit in range 2
        action = RangeAttack(self.game, {'source': self.game.hero, 'target_hex': '0;1'})
        self.assertEqual(action.execute(), {'range_attack': [{'target_hex': '0;1', 'damage': 5}]})
        # hit empty hex. Info about target is passed to ui for animation, but no info about damage dealt
        self.game.load_state()
        action = RangeAttack(self.game, {'source': self.game.hero, 'target_hex': '2;1'})
        self.assertEqual(action.execute(), {'range_attack': [{'target_hex': '2;1'}]})
        # hit obstacle
        self.game.load_state()
        action = RangeAttack(self.game, {'source': self.game.hero, 'target_hex': '1;1'})
        self.assertEqual(action.execute(), {'range_attack': [{'target_hex': '1;1'}]})

    def test_range_attack_failed(self):
        self.game.load_state()
        # hit unit out of distance
        action = RangeAttack(self.game, {'source': self.game.hero, 'target_hex': '0;0'})
        self.assertRaises(RuntimeError, action.execute)

    def test_path_of_fire(self):
        # one unit hit
        self.game.load_state()
        action = PathOfFire(self.game, {'source': self.game.hero, 'target_hex': '-1;4'})
        self.assertEqual(action.execute(), {'path_of_fire': [
            {'target_hex': '-1;4', 'damage': 8},
            {'target_hex': '-2;5'}
        ]})
        # two units hit
        self.game.load_state()
        action = PathOfFire(self.game, {'source': self.game.hero, 'target_hex': '0;2'})
        self.assertEqual(action.execute(), {'path_of_fire': [
            {'target_hex': '0;2'},
            {'target_hex': '0;1', 'damage': 8},
            {'target_hex': '0;0', 'damage': 8},
            {'target_hex': '0;-1'}
        ]})
        # no units full path hit
        self.game.load_state()
        action = PathOfFire(self.game, {'source': self.game.hero, 'target_hex': '-1;3'})
        self.assertEqual(action.execute(), {'path_of_fire': [
            {'target_hex': '-1;3'},
            {'target_hex': '-2;3'},
            {'target_hex': '-3;3'},
            {'target_hex': '-4;3'},
        ]})
        # no units hit with obstacle on a way
        self.game.load_state()
        action = PathOfFire(self.game, {'source': self.game.hero, 'target_hex': '1;2'})
        self.assertEqual(action.execute(), {'path_of_fire': [
            {'target_hex': '1;2'},
            {'target_hex': '2;1'}
        ]})
        # obstacle hit
        self.game.load_state()
        action = PathOfFire(self.game, {'source': self.game.hero, 'target_hex': '1;3'})
        self.assertEqual(action.execute(), {'path_of_fire': []})

    def test_path_of_fire_failed(self):
        self.game.load_state()
        action = PathOfFire(self.game, {'source': self.game.hero, 'target_hex': '-2;3'})
        self.assertRaises(RuntimeError, action.execute)

    def test_shield_bash(self):
        # one unit hit
        self.game.load_state()
        action = ShieldBash(self.game, {'source': self.game.hero, 'target_hex': '-1;3'})
        self.assertEqual(action.execute(), {'shield_bash': [
            {'target_hex': '-1;3', 'main_target': True},
            {'target_hex': '-1;4', 'damage': 5, 'pushed_to': '-2;5'},
        ]})
        # two unit hit
        self.game.load_state()
        action = ShieldBash(self.game, {'source': self.game.hero, 'target_hex': '-1;4'})
        sentenced_to_death = self.game.get_object_by_position('0;4').pk
        self.assertEqual(action.execute(), {'shield_bash': [
            {'target_hex': "-1;4", 'damage': 5, 'pushed_to': "-2;5", 'main_target': True},
            {'target_hex': "0;4", 'damage': 10},
        ]})
        self.assertNotIn(sentenced_to_death, self.game.units)
        # hit no units
        self.game.load_state()
        action = ShieldBash(self.game, {'source': self.game.hero, 'target_hex': '0;2'})
        self.assertEqual(action.execute(), {'shield_bash': [
            {'target_hex': '0;2', 'main_target': True}
        ]})

    def test_shield_bash_failed(self):
        self.game.load_state()
        action = ShieldBash(self.game, {'source': self.game.hero, 'target_hex': '-2;3'})
        self.assertRaises(RuntimeError, action.execute)

    def test_blink(self):
        self.game.load_state()
        action = Blink(self.game, {'source': self.game.hero, 'target_hex': '-2;2'})
        self.assertEqual(action.execute(), {'blink': [{'target_hex': '-2;2'}]})

    def test_blink_failed(self):
        # target too far
        self.game.load_state()
        action = Blink(self.game, {'source': self.game.hero, 'target_hex': '-3;2'})
        self.assertRaises(RuntimeError, action.execute)
        # blink on a unit
        self.game.load_state()
        action = Blink(self.game, {'source': self.game.hero, 'target_hex': '0;1'})
        self.assertRaises(RuntimeError, action.execute)
