class Exit:
    """Class to work with Exit building"""
    @staticmethod
    def build(game, structure):
        game.board.place_game_object(structure, f'{0};-{game.board.radius - 2}')


class Shop:
    @staticmethod
    def build(game, structure):
        pass


class StructuresManager:
    _structures_mapping = {
        'exit': Exit,
        'shop': Shop,
    }

    @staticmethod
    def build(game, structure_model):
        StructuresManager._structures_mapping[structure_model.code_name].build(game, structure_model)
