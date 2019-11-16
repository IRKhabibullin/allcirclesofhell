from ..models import GameModel
from django.contrib.auth.models import User
from game.mechanics.game_instance import GameInstance


class GameManager(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(GameManager, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.game_instances = {}

    def new_game(self, user_id):
        _user = User.objects.get(pk=user_id)
        _game = GameModel.objects.create(user=_user)
        game_instance = GameInstance(_game)
        self.game_instances[_game.pk] = game_instance
        return _game.pk

    def get_game(self, game_id):
        if game_id in self.game_instances:
            print(f'game {game_id} already loaded')
            self.game_instances[game_id].init_round()
            return self.game_instances[game_id]
        _game = GameModel.objects.get(pk=game_id)
        if _game:
            print(f'game {game_id} just loaded')
            game_instance = GameInstance(_game)
            game_instance.init_round()
            self.game_instances[game_id] = game_instance
            return game_instance
        print(f"game {game_id} doesn't exist")

    def get_games_by_user(self, user):
        games = GameModel.objects.filter(user=user)
        return games
