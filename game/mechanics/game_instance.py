import json
import math
from random import shuffle

from game.mechanics.actions import ActionManager, ActionNotAllowedError, Action, ActionResponse
from game.mechanics.game_objects import Hero, BaseGameObject, BaseUnitObject, Unit
from game.models import User, GameModel, UnitModel, HeroModel, ItemModel
from game.mechanics.board import Board, Hex
from game.mechanics.constants import slotHero, slotEmpty, slotUnit


class GameInstance:
    """
    Class to manage single game instance
    """
    def __init__(self, game_model: GameModel):
        """
        Loading board from passed game model or generating new
        """
        self._game = game_model
        game_state = json.loads(self._game.state)
        self.board = Board(**game_state.get('board', {}))
        self._hero = Hero(self._game.hero)
        self._units = {}

    @classmethod
    def new(cls, user: User, hero: dict):
        """Create new game but not save"""
        hero_model = HeroModel.objects.create(name=hero['name'],
                                              suit=ItemModel.objects.get(name='Cuirass'),
                                              weapon=ItemModel.objects.get(name='Sword'))
        _game = GameModel.objects.create(user=user, hero=hero_model)
        _instance = cls(_game)
        return _game.pk, _instance

    @classmethod
    def load(cls, game_id):
        """Load already created game"""
        _game = GameModel.objects.get(pk=game_id)
        if _game:
            return cls(_game)

    @property
    def hero(self):
        return self._hero

    @property
    def units(self):
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
        self._hero.moves = list(
            self.board.get_hexes_in_range(self._hero.position, self._hero.move_range, allowed=[slotEmpty]).keys())
        self._hero.attack_hexes = list(self.board.get_hexes_in_range(self._hero.position, self._hero.attack_range,
                                                                     allowed=[slotEmpty, slotUnit]).keys())
        for unit in self._units.values():
            unit.moves = list(self.board.get_hexes_in_range(unit.position, unit.move_range, allowed=[slotEmpty]).keys())
            unit.attack_hexes = list(self.board.get_hexes_in_range(unit.position, unit.attack_range,
                                                                   allowed=[slotEmpty, slotHero]).keys())

    def make_turn(self, action_data: dict):
        """Make game turn. First goes hero, then units"""
        response = ActionResponse(action_data['action'])
        # hero performs actions first
        try:
            action_data['source'] = self._hero
            action: Action = ActionManager.get_action(self, action_data)
            response.hero_data.update(action.execute())
        except RuntimeError as err:
            print('Hero action failed', err)
            response.state = 'failed'
        #  if fails then return failure and units doesnt act
        # units choose from available actions
        for unit in self._units.values():
            available_actions = ActionManager.available_actions(self, unit)
            chosen_action = ActionManager.get_action(self, unit.choose_action(available_actions))
            try:
                response.units_data[unit.pk].update(chosen_action.execute())
            except RuntimeError as err:
                print('Unit action failed', err)
        return response

    def get_game_objects(self, **kwargs):
        game_objects = {}
        if 'hero' in kwargs:
            game_objects['hero'] = self._hero
        if 'units' in kwargs:
            game_objects['units'] = {pk: unit for pk, unit in self._units.items() if pk in kwargs['units']}
        if 'hexes' in kwargs:
            game_objects['hexes'] = {hex_id: _hex for hex_id, _hex in self.board.items() if hex_id in kwargs['hexes']}
        return game_objects

    def hero_action(self, action_data: dict) -> dict:
        """
        Make hero action
        """
        # todo delete
        action_data['allowed'] = False
        try:
            action_result = ActionManager.execute(self, action_data)
        except ActionNotAllowedError:
            action_result = {'allowed': False}
        else:
            # update hero's and units' possible moves
            action_result['units_actions'] = self.units_action(except_list=action_result.pop('stunned_units', []))
            self.update_moves()
        return action_result

    def units_action(self, except_list: list) -> list:
        """
        Units' actions. Follows after hero's action
        except_list: list of unit ids. These units doesnt act this time
        """
        units_actions = []
        for unit in self._units.values():
            if unit.pk in except_list:
                continue
            # try to find target to attack
            targets = [hex_id for hex_id in unit.attack_hexes if self.board[hex_id].slot == slotHero]
            if targets:
                # suppose units can attack only hero for now
                attack_result = ActionManager.execute(self, {'action': 'attack', 'hero_attack': False,
                                                             'target_unit': unit.pk})
                if attack_result['allowed']:
                    units_actions.append({'source': str(unit.pk), 'damage_dealt': attack_result['damage']})
            else:
                # try to move somewhere
                self.unit_move(unit)
        return units_actions

    def unit_move(self, unit: UnitModel):
        """
        Unit's move
        """
        _move_pos = None
        remaining_moves = set(unit.moves)
        while remaining_moves:
            _move_pos = remaining_moves.pop()
            if self.board[_move_pos].slot == slotEmpty:
                break
        if _move_pos:
            self.board.place_game_object(unit, _move_pos)

    def damage_instance(self, source, target, damage):
        # apply damage modifiers
        # call pre-damage spells
        target.health -= damage
        # call after-damage spells
        return damage

    # region: game api
    def get_object_by_position(self, hex_id: str) -> BaseGameObject:
        """Get object position"""
        return self.board.get(hex_id).slot

    def move_object(self, game_object: BaseGameObject, new_position: str):
        """Moves object from <target_hex> to <new_position>"""
        self.board.place_game_object(game_object, new_position)

    def deal_damage(self, source: BaseUnitObject, target_hex: str, damage: int):
        """Deal <damage> to object in <target_hex>"""
        # if will add damage types, then <damage> arg must be a DamageInstance class, or something
        target = self.board.get(target_hex).slot
        target.receive_damage(damage)

    def distance(self, source: Hex, target_hex: str):
        return self.board.distance(source, self.board.get(target_hex))

    def get_hexes_in_range(self, start_hex: Hex, _range: int, **kwargs) -> dict:
        return self.board.get_hexes_in_range(start_hex, _range, **kwargs)
    # endregion
