import json
import math
from random import shuffle
from typing import Dict

from game.mechanics.actions import ActionManager, Action, ActionResponse
from game.mechanics.game_objects import Hero, BaseGameObject, BaseUnitObject, Unit
from game.models import User, GameModel, UnitModel, HeroModel, ItemModel
from game.mechanics.board import Board, Hex
from game.mechanics.constants import slotHero, slotEmpty, slotUnit


class GameInstance:
    """
    Class to manage single game instance
    """
    def __init__(self, game_model: GameModel):
        """Loading board from passed game model or generating new"""
        self._game = game_model
        game_state = json.loads(self._game.state)
        self.board = Board(**game_state.get('board', {}))
        self._hero = Hero(self._game.hero)
        self._units = {}

    @classmethod
    def new(cls, user: User, hero_data: dict):
        """
        Create new game but not save
        Returns game id and game instance itself
        """
        hero_model = HeroModel.objects.create(name=hero_data['name'],
                                              suit=ItemModel.objects.get(name='Cuirass'),
                                              weapon=ItemModel.objects.get(name='Sword'))
        _game = GameModel.objects.create(user=user, hero=hero_model)
        _instance = cls(_game)
        return _game.pk, _instance

    @classmethod
    def load(cls, game_id: int):
        """Load already created game"""
        _game = GameModel.objects.get(pk=game_id)
        if _game:
            return cls(_game)

    @property
    def hero(self) -> Hero:
        """Get game hero"""
        return self._hero

    @property
    def units(self) -> Dict[int, Unit]:
        """Get game units dict"""
        return self._units

    def init_round(self):
        """
        Initializing round
        Clearing the board
        Setting hero position
        Counting and placing units
        """
        self._units = {}
        self.board.clear_board()
        self.board.place_game_object(self._hero, f'0;{self.board.radius // 2}')
        self.board.set_obstacles()

        available_hexes = {_id for _id, _hex in self.board.items() if _hex.slot == slotEmpty}
        # area around hero, where units must not be placed
        safe_range = max(self.board.radius // 2 - self._game.round // 8, 1)
        hexes_in_range = self.board.get_hexes_in_range(self._hero.position, safe_range, allowed=[slotEmpty, slotHero])
        available_hexes = list(available_hexes - hexes_in_range.keys())
        shuffle(available_hexes)

        def place_units(points: int, unit_level: int):
            """
            Counting units of current level and placing them on board.
            About half of remaining points goes to current level of units if its not 1 level unit
            Recursive call for units of lower level
            """
            u_count = points if unit_level == 1 else round((points // 2) / unit_level)
            for i in range(u_count):
                unit = UnitModel.objects.get(level=unit_level)
                unit.pk = len(self._units)
                unit = Unit(unit)
                self.board.place_game_object(unit, available_hexes.pop())
                self._units[unit.pk] = unit
            points_remain = int(points - u_count * unit_level)
            if points_remain:
                place_units(points_remain, unit_level // 2)

        max_unit_level = int(math.pow(2, math.floor(math.log2(self._game.round / 2)))) or 1
        place_units(self._game.round, max_unit_level)
        self.update_moves()

    def update_moves(self):
        """Update available moves and attack hexes of hero and units"""
        self._hero.moves = list(
            self.board.get_hexes_in_range(self._hero.position, self._hero.move_range, allowed=[slotEmpty]).keys())
        self._hero.attack_hexes = list(self.board.get_hexes_in_range(self._hero.position, self._hero.attack_range,
                                                                     allowed=[slotEmpty, slotUnit]).keys())
        for unit in self._units.values():
            unit.moves = list(self.board.get_hexes_in_range(unit.position, unit.move_range, allowed=[slotEmpty]).keys())
            unit.attack_hexes = list(self.board.get_hexes_in_range(unit.position, unit.attack_range,
                                                                   allowed=[slotEmpty, slotHero]).keys())

    def make_turn(self, action_data: dict) -> ActionResponse:
        """Make game turn. First goes hero, then units"""
        response = ActionResponse(action_data['action'])
        # hero performs actions first
        try:
            action_data['source'] = self._hero
            action: Action = ActionManager.get_action(self, action_data)
            response.hero_actions.update(action.execute())
        except RuntimeError as err:
            print('Hero action failed', err)
            response.state = 'failed'
        # if fails then return failure and units doesnt act
        if response.state != 'failed':
            for unit in self._units.values():
                # units choose from available actions
                available_actions = ActionManager.available_actions(self, unit)
                chosen_action = ActionManager.get_action(self, unit.choose_action(available_actions))
                try:
                    response.units_actions[unit.pk].update(chosen_action.execute())
                except RuntimeError as err:
                    print('Unit action failed', err)
        self.update_moves()
        return response

    # region: game api
    def get_object_by_position(self, hex_id: str) -> BaseGameObject:
        """Get object position"""
        _hex = self.board.get(hex_id)
        if _hex:
            return _hex.slot

    def move_object(self, game_object: BaseGameObject, new_position: str):
        """Moves object from <target_hex> to <new_position>"""
        self.board.place_game_object(game_object, new_position)

    def deal_damage(self, target_hex: str, damage: int):
        """Deal <damage> to object in <target_hex>"""
        # if will add damage types, then <damage> arg must be a DamageInstance class, or something
        target = self.board.get(target_hex).slot
        if isinstance(target, BaseUnitObject):
            target.receive_damage(damage)
            if target.health <= 0:
                self.destroy_unit(target)

    def destroy_unit(self, target: BaseUnitObject):
        """Remove unit from game. Called on units death"""
        self.board.get_object_position(target).slot = slotEmpty
        if isinstance(target, Unit):
            del self._units[target.pk]

    def distance(self, source: Hex, target_hex: str) -> int:
        """Get distance between two hexes"""
        return self.board.distance(source, self.board.get(target_hex))

    def get_hexes_in_range(self, start_hex: Hex, _range: int, **kwargs) -> Dict[str, Hex]:
        """
        Get hexes in <_range> away from <start_hex>. <start_hex> hex itself doesn't count in range
        Can specify allowed hex occupation in kwargs, or filter them separately with according method
        """
        return self.board.get_hexes_in_range(start_hex, _range, **kwargs)

    def get_hex(self, hex_id: str, default_value=None) -> Hex:
        """Get hex by it's id"""
        return self.board.get(hex_id, default_value)
    # endregion
