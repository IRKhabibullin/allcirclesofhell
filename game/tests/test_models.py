from django.test import TestCase
from django.contrib.auth.models import User
from game.models import GameInstance


class GameInstanceTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="admin")
        self.game_instance = GameInstance.objects.create(user=self.user1)
        self.game_instance.init_board()

    def test_board_created(self):
        self.assertTrue(self.game_instance.board)
