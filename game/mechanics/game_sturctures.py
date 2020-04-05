from random import randrange
from typing import TYPE_CHECKING, Dict

from game.mechanics.board import Board
from game.mechanics.game_objects import InteractiveGameObject
from game.models import GameStructureModel

if TYPE_CHECKING:
    from game.mechanics.game_instance import GameInstance


class BaseStructure(InteractiveGameObject):
    """Base structure class"""
    structure_name: str

    def __init__(self, object_model):
        super().__init__(object_model)
        self.position = ''

    def find_position(self, board: 'Board'):
        # todo make normal positioning
        return f'{randrange(-board.radius, board.radius)};{randrange(-board.radius, board.radius)}'


class Exit(BaseStructure):
    """Class to work with Exit building"""
    def find_position(self, board: 'Board'):
        return f'{0};-{board.radius - 2}'


class Shop(BaseStructure):
    """Some shop"""
    pass


class StructuresManager:
    _structures_mapping: Dict[str, BaseStructure.__class__] = {
        'exit': Exit,
        'shop': Shop,
    }

    @staticmethod
    def build(game: 'GameInstance', structure_model: 'GameStructureModel', position: str = None) -> BaseStructure:
        structure = StructuresManager._structures_mapping[structure_model.code_name](structure_model)
        if position is not None:
            game.move_object(structure, position)
        else:
            game.move_object(structure, structure.find_position(game._board))
        return structure
