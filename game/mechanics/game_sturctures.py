from typing import TYPE_CHECKING, Dict, List
from game.mechanics.constants import slotStructure
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

    def __str__(self):
        return slotStructure


class Exit(BaseStructure):
    """Exit from round"""
    pass


class Shop(BaseStructure):
    """Some shop"""
    pass


class StructuresManager:
    _structures_mapping: Dict[str, BaseStructure.__class__] = {
        'exit': Exit,
        'shop': Shop,
    }

    @classmethod
    def place_structures(cls, game: 'GameInstance', available_hexes: List[str], exit_position: str):
        for structure_model in GameStructureModel.objects.all():
            if game.round % structure_model.round_frequency == 0:
                position = exit_position if structure_model.code_name == 'exit' else available_hexes.pop()
                structure = cls.build(game, structure_model, position)
                game.structures[structure_model.code_name] = structure

    @classmethod
    def build(cls, game: 'GameInstance', structure_model: GameStructureModel, position: str) -> BaseStructure:
        structure = cls._structures_mapping[structure_model.code_name](structure_model)
        game.move_object(structure, position)
        return structure
