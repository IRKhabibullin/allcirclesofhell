from django.test import TestCase
from django.contrib.auth.models import User
from game.models import GameModel


class GameInstanceTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="admin")
        self.game_model = GameModel.objects.create(user=self.user1)

    def test_board_created(self):
        self.assertTrue(self.game_model.user == self.user1)
