"""
Functions for actions
"""


def attack(game, source, target):
    """Simple melee attack"""
    hero_hex = game.board.hexes[source.position]
    target_hex = game.board.hexes[target.position]
    if game.board.distance(hero_hex, target_hex) > source.attack_range:
        return False
    game.damage_instance(source, target, source.damage)
    return True
