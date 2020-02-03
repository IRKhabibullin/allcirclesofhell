import json
import math
from random import shuffle

from game.mechanics.actions import ActionManager, ActionNotAllowedError
from game.mechanics.game_sturctures import StructuresManager
from game.models import User, GameModel, Unit, Hero, Item, GameStructure
from game.mechanics.board import Board
from game.mechanics.constants import ocpHero, ocpEmpty, ocpUnit


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

        # round-wise game objects
        self.units = {}
        self.structures = []

    @classmethod
    def new(cls, user: User, hero: dict):
        """Create new game but not save"""
        hero = Hero.objects.create(name=hero['name'], weapon=Item.objects.get(name='Sword'),
                                   suit=Item.objects.get(name='Cuirass'))
        _game = GameModel.objects.create(user=user, hero=hero)
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
        return self._game.hero

    def init_round(self):
        """
        Initializing round
        Clearing the board
        Setting hero position
        Counting and placing units
        """
        self.units = {}
        self.structures = {}
        self.board.clear_board()
        self.board.place_game_object(self.hero, f'0;{self.board.radius // 2}')

        available_hexes = {_id for _id, _hex in self.board.items() if _hex.occupied_by == ocpEmpty}
        # area around hero, where units must not be placed
        clear_area_range = max(self.board.radius // 2 - self._game.round // 8, 1)
        hexes_in_range = self.board.get_hexes_in_range(self.hero.position, clear_area_range, [ocpEmpty, ocpHero])
        available_hexes = list(available_hexes - hexes_in_range.keys())
        shuffle(available_hexes)

        def place_structures():
            for structure in GameStructure.objects.all():
                if self._game.round % structure.round_frequency == 0:
                    StructuresManager.build(self, structure)
                    self.structures[structure.pk] = structure

        def place_units(points: int, unit_cost: int):
            """
            Counting units of current <unit_cost> and placing them on board.
            About half of <points> goes to units of current <unit_cost> if unit_cost != 1
            Recursive call for units of lower cost
            """
            u_count = points if unit_cost == 1 else round((points // 2) / unit_cost)
            for i in range(u_count):
                unit = Unit.objects.get(level=unit_cost)
                unit.pk = len(self.units)
                self.board.place_game_object(unit, available_hexes.pop())
                self.units[unit.pk] = unit
            points_remain = int(points - u_count * unit_cost)
            if points_remain:
                place_units(points_remain, unit_cost // 2)

        max_unit_cost = int(math.pow(2, math.floor(math.log2(self._game.round / 2)))) or 1
        place_structures()
        place_units(self._game.round, max_unit_cost)
        self.update_moves()

    def update_moves(self):
        self.hero.moves = list(
            self.board.get_hexes_in_range(self.hero.position, self.hero.move_range, [ocpEmpty]).keys())
        self.hero.attack_hexes = list(self.board.get_hexes_in_range(self.hero.position, self.hero.attack_range,
                                                                    [ocpEmpty, ocpUnit]).keys())
        for unit in self.units.values():
            unit.moves = list(self.board.get_hexes_in_range(unit.position, unit.move_range, [ocpEmpty]).keys())
            unit.attack_hexes = list(self.board.get_hexes_in_range(unit.position, unit.attack_range,
                                                                   [ocpEmpty, ocpHero]).keys())

    def hero_action(self, action_data: dict) -> dict:
        """
        Make hero action
        """
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
        for unit in self.units.values():
            if unit.pk in except_list:
                continue
            # try to find target to attack
            targets = [hex_id for hex_id in unit.attack_hexes if self.board[hex_id].occupied_by == ocpHero]
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

    def unit_move(self, unit: Unit):
        """
        Unit's move
        """
        _move_pos = None
        remaining_moves = set(unit.moves)
        while remaining_moves:
            _move_pos = remaining_moves.pop()
            if self.board[_move_pos].occupied_by == ocpEmpty:
                break
        if _move_pos:
            self.board.place_game_object(unit, _move_pos)

    def damage_instance(self, source, target, damage):
        # apply damage modifiers
        # call pre-damage spells
        target.health -= damage
        # call after-damage spells
        if target.health <= 0:
            self.on_death(target)
        return damage

    def on_death(self, target):
        if isinstance(target, Hero):
            # game over
            pass
        elif isinstance(target, Unit):
            target.position.occupied_by = ocpEmpty
            del self.units[target.pk]
