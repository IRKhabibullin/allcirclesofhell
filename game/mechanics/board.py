from random import random
from typing import TYPE_CHECKING, Dict, List
from game.mechanics.constants import BOARD_RADIUS, slotEmpty, slotObstacle
from game.mechanics.game_objects import Obstacle

if TYPE_CHECKING:
    from game.mechanics.game_objects import BaseGameObject

# chances in percents
OBSTACLE_CHANCE = 15


class Hex:
    """
    Hex object, used in board
    """
    def __init__(self, q: int, r: int, slot: 'BaseGameObject' = slotEmpty):
        self.q = q
        self.r = r

        self.x = q
        self.y = -q - r
        self.z = r

        self.slot = slot

    @property
    def id(self) -> str:
        """Hex id"""
        return f'{self.q};{self.r}'

    def distance_from_center(self) -> int:
        """Distance from current hex to the center of board"""
        return max(abs(self.x), abs(self.y), abs(self.z))

    def __str__(self):
        return f'Hex({self.id}|{self.slot})'

    def __repr__(self):
        return f'Hex({self.id}|{self.slot})'

    def as_dict(self) -> dict:
        """Serialized representation"""

        return {'q': self.q, 'r': self.r, 'slot': str(self.slot)}


class Board:
    """
    Game board, made of hexes, positioned in hexagonal form
    """
    position_biases = [
        (1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)
    ]

    def __init__(self, radius: int = BOARD_RADIUS):

        def create_neighbors(_hex: Hex):
            """
            Method generating grid of hexes in board
            """
            for bias in self.position_biases:
                new_pos = [sum(x) for x in zip((_hex.q, _hex.r), bias)]
                new_id = f'{new_pos[0]};{new_pos[1]}'
                if new_id in self.__hexes:
                    continue
                new_hex = Hex(*new_pos)
                if self.add(new_hex):
                    create_neighbors(new_hex)

        self.radius = radius
        self.__hexes = {}
        start_hex = Hex(0, 0)
        self.add(start_hex)
        create_neighbors(start_hex)

    def load_state(self, hexes: list):
        """Load board from saved state"""
        for _hex_data in hexes:
            _hex = Hex(_hex_data['q'], _hex_data['r'])
            if _hex_data['slot'] == slotObstacle:
                _hex.slot = Obstacle()
            self.add(_hex)

    def add(self, _hex: Hex) -> bool:
        """
        Add/update hex to board, if hex is in radius of board
        Returns success of operation
        """
        if isinstance(_hex, Hex) and _hex.distance_from_center() < self.radius:
            self.__hexes[f'{_hex.q};{_hex.r}'] = _hex
            return True
        return False

    def __getitem__(self, key: str) -> Hex:
        return self.__hexes[key]

    def get(self, key: str, default_value=None) -> Hex:
        """Returns hex by its key."""
        return self.__hexes.get(key, default_value)

    def __contains__(self, _hex: str) -> bool:
        return _hex in self.__hexes

    def __iter__(self):
        for _hex in self.__hexes:
            yield _hex

    def items(self):
        """Returns items of dict with all hexes in board"""
        return self.__hexes.items()

    def get_neighbors(self, _hex: Hex) -> List[Hex]:
        """
        Get neighboring hexes.
        Up to 6 neighbors for given hex (Could be on the edge of board and will have less neighbors)
        """
        _neighbors = []
        for bias in self.position_biases:
            _neighbor = self.get(f"{_hex.q + bias[0]};{_hex.r + bias[1]}")
            if _neighbor:
                _neighbors.append(_neighbor)
        return _neighbors

    def get_hexes_in_range(self, start_hex: Hex, _range: int, **kwargs) -> Dict[str, Hex]:
        """
        Get hexes in <_range> away from <start_hex>. <start_hex> hex itself doesn't count in range
        Can specify allowed hex occupation in kwargs, or filter them separately with according method
        """
        hexes_in_range = {}
        for q in range(-_range, _range + 1):
            for r in range(max(-_range, -q - _range), min(_range, -q + _range) + 1):
                _hex_id = f"{q + start_hex.q};{r + start_hex.r}"
                hexes_in_range[_hex_id] = self.get(_hex_id)
        return self.filter(hexes_in_range, **kwargs)

    def filter(self, hexes: dict, **kwargs) -> Dict[str, Hex]:
        """Filter passed hexes by their slots"""
        for hex_id in list(hexes.keys()):
            if hex_id not in self.__hexes:
                del hexes[hex_id]
        if 'allowed' in kwargs:
            hexes = {hex_id: _hex for hex_id, _hex in hexes.items() if str(_hex.slot) in kwargs['allowed']}
        if 'restricted' in kwargs:
            hexes = {hex_id: _hex for hex_id, _hex in hexes.items() if str(_hex.slot) not in kwargs['restricted']}
        return hexes

    def place_game_object(self, game_object: 'BaseGameObject', hex_id: str):
        """Place game object in board according to it's position"""
        if hex_id in self.__hexes:
            _hex = self.__hexes[hex_id]
            if _hex.slot != slotEmpty and _hex.slot != game_object:
                raise RuntimeError('Cant move there. Hex already occupied')
            if game_object.position:
                game_object.position.slot = slotEmpty
            game_object.position = _hex
            _hex.slot = game_object
        else:
            raise RuntimeError('No such hex on board')

    def get_object_position(self, game_object: 'BaseGameObject') -> Hex:
        """Find hex that stores passed game object"""
        for _hex in self.__hexes.values():
            if _hex.slot == game_object:
                return _hex

    def clear_board(self):
        """Clear board from units, hero, game objects. Re-generate obstacles"""
        # todo move obstacles generating into function and call it separately
        for _hex in self.__hexes.values():
            if _hex.slot != slotEmpty:
                _hex.slot.position = None
            _hex.slot = slotEmpty

    def set_obstacles(self):
        """Generates obstacles on board"""
        # todo write algorithms for obstacles generating
        for _hex in self.__hexes.values():
            if _hex.slot == slotEmpty:
                if int(random() * 100) < OBSTACLE_CHANCE:
                    _hex.slot = Obstacle()

    @staticmethod
    def distance(hex_a: Hex, hex_b: Hex) -> int:
        """Get distance between two hexes"""
        return max(abs(hex_a.x - hex_b.x), abs(hex_a.y - hex_b.y), abs(hex_a.z - hex_b.z))

    def get_state(self) -> dict:
        """Get serialized board state"""
        return {'radius': self.radius, 'hexes': {k: v.as_dict() for k, v in self.items()}}
