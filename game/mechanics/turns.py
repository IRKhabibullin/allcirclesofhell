from game.mechanics.game_instance import GameInstance


class Turn:
    def __init__(self, game_instance: GameInstance):
        self.game = game_instance
        self.hero_action = HeroAction(game_instance.hero)
        self._unit_actions = [UnitAction(unit for unit in game_instance.units)]

    def execute(self):
        self.hero_action.execute()


class HeroAction:
    def __init__(self, hero):
        self.hero = hero

    def execute(self):
        self


class UnitAction:
    def __init__(self, unit):
        self.unit = unit
