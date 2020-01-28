from ..models import GameModel
from django.contrib.auth.models import User
from game.mechanics.game_instance import GameInstance


class GameManager(object):
    """
    Singleton class to manage game instances
    """
    __instance = None

    @staticmethod
    def instance():
        """ Static access method. """
        if GameManager.__instance is None:
            GameManager()
        return GameManager.__instance

    def __init__(self):
        if GameManager.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            GameManager.__instance = self
        self.game_instances = {}

    def new_game(self, user_id: int) -> int:
        """
        Create new game and bind user to it. Returns game id
        """
        _user = User.objects.get(pk=user_id)
        _game = GameModel.objects.create(user=_user)
        game_instance = GameInstance(_game)
        self.game_instances[_game.pk] = game_instance
        return _game.pk

    def get_game(self, game_id: int) -> GameInstance:
        """
        Get loaded game or query from db already existing game
        """
        if game_id in self.game_instances:
            return self.game_instances[game_id]
        _game = GameModel.objects.get(pk=game_id)
        if _game:
            game_instance = GameInstance(_game)
            self.game_instances[game_id] = game_instance
            return game_instance

    @staticmethod
    def get_games_by_user(user: User) -> list:
        """
        Get list of games of given user
        """
        games = GameModel.objects.filter(user=user)
        return games
