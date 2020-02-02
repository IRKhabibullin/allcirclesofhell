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
        """Static access method"""
        if GameManager.__instance is None:
            GameManager()
        return GameManager.__instance

    def __init__(self):
        if GameManager.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            GameManager.__instance = self
        self.game_instances = {}

    def new_game(self, user: User, hero: dict) -> int:
        """Create new game and bind user to it. Returns game id"""
        game_id, game_instance = GameInstance.new(user, hero)
        self.game_instances[game_id] = game_instance
        return game_instance

    def get_game(self, game_id: int) -> GameInstance:
        """Get loaded game or query already existing game from db"""
        if game_id in self.game_instances:
            return self.game_instances[game_id]
        game_instance = GameInstance.load(game_id)
        if game_instance:
            self.game_instances[game_id] = game_instance
            return game_instance

    def delete_game(self, game_id: int) -> bool:
        if game_id in self.game_instances:
            _game = self.game_instances[game_id]
            del self.game_instances[game_id]
        else:
            _game = GameModel.objects.filter(pk=game_id)
            if not _game:
                return False
            _game = _game[0]
        del_count, del_objects = _game.hero.delete(keep_parents=False)
        # del_count, del_objects = self.game_instances[game_id].delete()
        print(f'Deleted {del_count} objects: {del_objects}')
        return bool(del_count)


    @staticmethod
    def get_games_by_user(user: User) -> list:
        """Get list of games of given user"""
        games = GameModel.objects.filter(user=user)
        return games
