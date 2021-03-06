import json
import math
from random import shuffle
from typing import Dict

from game.mechanics.actions import ActionManager, Action, ActionResponse
from game.mechanics.game_objects import Hero, BaseGameObject, BaseUnitObject, Unit
from game.mechanics.game_sturctures import StructuresManager
from game.models import User, GameModel, UnitModel, HeroModel, ItemModel, GameStructureModel, HandbookModel, \
    AbilityModel, SpellModel, SkillModel
from game.mechanics.board import Board, Hex
from game.mechanics.constants import slotHero, slotEmpty, slotUnit, slotObstacle


class GameInstance:
    """
    Class to manage single game instance
    """
    def __init__(self, game_model: GameModel):
        """Loading board from passed game model or generating new"""
        self._game = game_model
        self._board = Board()
        self._hero = Hero(self._game.hero)

        # round-wise game objects
        self.units = {}
        self.structures = {}

    # region instance managing
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

    def save_state(self):
        """Save state of the game"""
        # need to save hero spells/skills/items too
        game_state = {
            'round': self._game.round,
            'hero': {'health': self.hero.health, 'position': self.hero.position.id},
            'hexes': [],
            'units': [],
            'structures': [],
        }
        for hex_id, _hex in self._board.items():
            if str(_hex.slot) == slotObstacle:
                game_state['hexes'].append({'q': _hex.q, 'r': _hex.r, 'slot': slotObstacle})
        for unit_id, unit in self.units.items():
            game_state['units'].append({'level': unit.level, 'health': unit.health, 'position': unit.position.id})
        for code_name, structure in self.structures.items():
            game_state['structures'].append({'code_name': code_name, 'position': structure.position.id})
        self._game.state = json.dumps(game_state)
        self._game.save()

    def load_state(self):
        """Load saved state of the game"""
        game_state = json.loads(self._game.state)

        self._game.round = game_state.get('round', self._game.round)
        self.units.clear()
        self.structures.clear()
        self._board.clear_board()
        hero = game_state.get('hero', {})
        self.hero.set_health(hero.get('health', self.hero.health))
        self._board.place_game_object(self._hero, hero.get('position', f'0;{self._board.radius // 2}'))
        self._board.load_state(game_state.get('hexes', []))
        if 'structures' in game_state:
            for structure_data in game_state.get('structures', []):
                structure_model = GameStructureModel.objects.get(code_name=structure_data['code_name'])
                structure = StructuresManager.build(self, structure_model, structure_data['position'])
                self.structures[structure_model.code_name] = structure
        if 'units' in game_state:
            for unit_data in game_state.get('units', []):
                unit = UnitModel.objects.get(level=unit_data['level'])
                unit.pk = len(self.units)
                unit.health = unit_data['health']
                unit = Unit(unit)
                self._board.place_game_object(unit, unit_data['position'])
                self.units[unit.pk] = unit
        self.update_moves()

    def before_closed(self):
        """
        Prepare game instance to be closed.
        Like remove hero's added spells, if he didn't finish the round, where he got them
        """
        self.hero.remove_unsaved_abilities()
    # endregion instance managing

    # region properties
    @property
    def round(self):
        return self._game.round

    @property
    def hero(self) -> Hero:
        return self._hero
    # endregion properties

    # region round managing
    def start_round(self):
        """
        Initializing round
        Clearing the board
        Setting hero position
        Counting and placing units
        """
        # clear everything round-vise
        self._board.clear_board()
        self.units.clear()
        self.structures.clear()

        # place objects for a new round
        self.move_object(self._hero, f'0;{self._board.radius // 2}')

        StructuresManager.place_structures(self, self.get_available_hexes(), f'{0};-{self._board.radius - 2}')
        self._board.set_obstacles()
        self.place_units()
        self.update_moves()

    def get_available_hexes(self) -> list:
        """
        Find hexes, where game objects could spawn.
        They must be in some distance from hero so he won't be attacked by all units at start and die instantly
        """
        # secure fixed place for exit
        exit_pos = f'{0};-{self._board.radius - 2}'
        available_hexes = {_id for _id, _hex in self._board.items() if _hex.slot == slotEmpty and _id != exit_pos}
        safe_range = max(self._board.radius // 2 - self._game.round // 8, 1)
        safe_hexes = self._board.get_hexes_in_range(self._hero.position, safe_range, allowed=[slotEmpty, slotHero])
        available_hexes = list(available_hexes - safe_hexes.keys())
        shuffle(available_hexes)
        return available_hexes

    def place_units(self):
        """Place units based on current game level"""

        def place_by_unit_level(points: int, unit_level: int, _available_hexes: list):
            """
            Counting units of current level and placing them on board.
            About half of remaining points goes to current level of units if its not 1 level unit
            Recursive call for units of lower level
            """
            u_count = points if unit_level == 1 else round((points // 2) / unit_level)
            for i in range(u_count):
                unit = UnitModel.objects.get(level=unit_level)
                unit.pk = len(self.units)
                unit = Unit(unit)
                self._board.place_game_object(unit, _available_hexes.pop())
                self.units[unit.pk] = unit
            points_remain = int(points - u_count * unit_level)
            if points_remain:
                place_by_unit_level(points_remain, unit_level // 2, _available_hexes)

        max_unit_level = int(math.pow(2, math.floor(math.log2(self._game.round / 2)))) or 1
        place_by_unit_level(self._game.round, max_unit_level, self.get_available_hexes())

    def update_moves(self):
        """Update available moves and attack hexes of hero and units"""
        self._hero.moves = list(
            self.get_hexes_in_range(self._hero.position, self._hero.move_range, allowed=[slotEmpty]).keys())
        self._hero.attack_hexes = list(self.get_hexes_in_range(self._hero.position, self._hero.attack_range,
                                                               allowed=[slotEmpty, slotUnit]).keys())
        for unit in self.units.values():
            unit.moves = list(self.get_hexes_in_range(unit.position, unit.move_range, allowed=[slotEmpty]).keys())
            unit.attack_hexes = list(self.get_hexes_in_range(unit.position, unit.attack_range,
                                                             allowed=[slotEmpty, slotHero]).keys())

    def make_turn(self, action_data: dict) -> ActionResponse:
        """Make game turn. First goes hero, then units"""
        response = ActionResponse(action_data['action'])
        # hero performs actions first
        try:
            action_data['source'] = self._hero
            action: Action = ActionManager.get_action(self, action_data)
            action_result = action.execute()
            response.hero_actions.update(action_result)
            if response.name in ['exit', 'sanctuary', 'shop']:
                # actions that shouldn't be followed by units' actions
                return response
        except RuntimeError as err:
            response.state = ActionResponse.FAILED
            return response
        # if fails then return failure and units doesnt act
        for unit in self.units.values():
            # units choose from available actions
            available_actions = ActionManager.available_actions(self, unit)
            chosen_action = ActionManager.get_action(self, unit.choose_action(available_actions))
            try:
                response.units_actions[unit.pk].update(chosen_action.execute())
                if self.is_game_over():
                    response.state = ActionResponse.GAME_OVER
            except RuntimeError as err:
                print('Unit action failed', err)
        self.update_moves()
        return response

    def is_game_over(self) -> bool:
        return self._hero.health <= 0

    def exit_round(self):
        """Finish current round"""
        self._game.round += 1
        self._game.save()
        self.hero.keep_unsaved_abilities()
        self.start_round()
    # endregion round managing

    # region game api
    def get_object_by_position(self, hex_id: str) -> BaseGameObject:
        """Get object position. If no such hex, KeyError raised"""
        return self._board[hex_id].slot

    def move_object(self, game_object: BaseGameObject, new_position: str):
        """Moves object from <target_hex> to <new_position>"""
        self._board.place_game_object(game_object, new_position)

    def add_ability(self, ability_type: str, code_name: str):
        """Add spell/skill/item to hero"""
        abilities_map = {
            'spell': SpellModel,
            'skill': SkillModel,
            'item': ItemModel
        }
        ability = abilities_map[ability_type].objects.get(code_name=code_name)
        self.hero.add_ability(ability_type, ability)

    def deal_damage(self, target_hex: str, damage: int) -> int:
        """Deal <damage> to object in <target_hex>"""
        # if will add damage types, then <damage> arg must be a DamageInstance class, or something
        try:
            target = self._board.get(target_hex).slot
            if isinstance(target, BaseUnitObject):
                target.receive_damage(damage)
                if target.health <= 0:
                    self.destroy_unit(target)
                return damage
        except Exception:
            # if for some reason it failed, then just do nothing (as if damage source hit the air)
            print(f'Damage dealing at target {target_hex} failed')

    def destroy_unit(self, target: BaseUnitObject):
        """Remove unit from game. Called on units death"""
        target.position.slot = slotEmpty
        if isinstance(target, Unit):
            del self.units[target.pk]

    def distance(self, source: Hex, target_hex: str) -> int:
        """Get distance between two hexes. If no target_hex on board, then exception raised"""
        return self._board.distance(source, self._board[target_hex])

    def get_hexes_in_range(self, start_hex: Hex, _range: int, **kwargs) -> Dict[str, Hex]:
        """
        Get hexes in <_range> away from <start_hex>. <start_hex> hex itself doesn't count in range
        Can specify allowed hex occupation in kwargs, or filter them separately with according method
        """
        return self._board.get_hexes_in_range(start_hex, _range, **kwargs)

    def get_hex(self, hex_id: str, default_value=None) -> Hex:
        """Get hex by it's id"""
        return self._board.get(hex_id, default_value)
    # endregion game api
