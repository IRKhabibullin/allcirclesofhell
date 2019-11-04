from ..models import GameInstance
from django.contrib.auth.models import User


class GameManager(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(GameManager, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.game_instances = {}

    def new_game(self, user_id):
        game_instance = GameInstance()
        user = User.objects.get(pk=user_id)
        game_instance.user = user
        game_instance.save()
        self.game_instances[game_instance.pk] = game_instance
        return game_instance

    def get_game(self, game_id):
        if game_id in self.game_instances:
            self.game_instances[game_id].init_board()
            return self.game_instances[game_id]
        game_instance = GameInstance.objects.get(pk=game_id)
        if game_instance:
            game_instance.init_board()
            self.game_instances[game_instance.pk] = game_instance
            return game_instance

    def get_games_by_user(self, user):
        games = GameInstance.objects.filter(user=user)
        return games
