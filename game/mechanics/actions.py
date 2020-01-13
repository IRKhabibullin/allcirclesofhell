"""
Functions for actions
"""


def attack(game, source, target):
    """Simple melee attack"""
    hero_hex = game.board.hexes[source.position]
    target_hex = game.board.hexes[target.position]
    if game.board.distance(hero_hex, target_hex) > source.attack_range:
        return {'allowed': False}
    damage_dealt = game.damage_instance(source, target, source.damage)
    return {'allowed': True, 'damage': damage_dealt}


def range_attack(game, source, target):
    """Simple range attack"""
    hero_hex = game.board.hexes[source.position]
    target_hex = game.board.hexes[target.position]
    if game.board.distance(hero_hex, target_hex) > source.attack_range + 1:
        return {'allowed': False}
    damage_dealt = game.damage_instance(source, target, source.damage)
    return {'allowed': True, 'damage': damage_dealt}


def path_of_fire(game_instance, action_data):
    """Path of fire spell"""
    result = {'allowed': False}
    start_hex = game_instance.board.hexes.get(action_data['target_hex'], None)
    hero_hex = game_instance.board.hexes[game_instance.game.hero.position]
    if not start_hex or game_instance.board.distance(hero_hex, start_hex) != 1:
        return result
    result['allowed'] = True
    dq, dr = start_hex['q'] - hero_hex['q'], start_hex['r'] - hero_hex['r']
    target_hexes = []
    targets = []
    for i in range(1, 5):
        hex_id = f"{hero_hex['q'] + dq * i};{hero_hex['r'] + dr * i}"
        _hex = game_instance.board.hexes.get(hex_id, None)
        if not _hex or _hex['occupied_by'] == 'obstacle':
            break
        target_hexes.append(hex_id)
        if _hex['occupied_by'] == 'unit':
            targets.append(hex_id)
    targets = {_unit.pk: {} for _unit in game_instance.units.values() if _unit.position in targets}
    print('path of fire targets:', list(targets.keys()))
    for _unit_id in targets:
        targets[_unit_id]['damage'] = game_instance.damage_instance(game_instance.game.hero,
                                                                    game_instance.units[_unit_id], 8)
    result['targets'] = targets
    result['target_hexes'] = target_hexes
    return result
