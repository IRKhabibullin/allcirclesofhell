from ..models import GameInstance


class GameManager(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(GameManager, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.game_instances = {}

    def new_game(self):
        game_instance = GameInstance()
        game_instance.save()
        self.game_instances[game_instance.pk] = game_instance
        return game_instance
