"""
Functions for actions
"""


def attack(game, hero, target):
    """Simple melee attack"""
    hero_hex = game.board.hexes[hero.position]
    target_hex = game.board.hexes[target.position]
    if game.board.distance(hero_hex, target_hex) > hero.attack_range:
        return False
    game.damage_instance(hero, target, hero.damage)
    return True
