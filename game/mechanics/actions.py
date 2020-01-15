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
    target_hexes, targets = [], []
    for i in range(1, 5):
        hex_id = f"{hero_hex['q'] + dq * i};{hero_hex['r'] + dr * i}"
        _hex = game_instance.board.hexes.get(hex_id, None)
        if not _hex or _hex['occupied_by'] == 'obstacle':
            break
        target_hexes.append(hex_id)
        if _hex['occupied_by'] == 'unit':
            targets.append(hex_id)
    targets = {_unit.pk: {} for _unit in game_instance.units.values() if _unit.position in targets}
    for _unit_id in targets:
        targets[_unit_id]['damage'] = game_instance.damage_instance(game_instance.game.hero,
                                                                          game_instance.units[_unit_id], 8)
    result['targets'] = targets
    result['target_hexes'] = target_hexes
    return result


def shield_bash(game_instance, action_data):
    """Shield bash spell"""
    result = {'allowed': False}
    start_hex = game_instance.board.hexes.get(action_data['target_hex'])
    hero_hex = game_instance.board.hexes[game_instance.game.hero.position]
    if not start_hex or game_instance.board.distance(hero_hex, start_hex) != 1:
        return result
    result['allowed'] = True
    target_hexes = list(set(game_instance.board.get_hexes_in_range(start_hex, 1)).intersection(
        game_instance.board.get_hexes_in_range(hero_hex, 1)) - {game_instance.game.hero.position})
    print('target hexes', target_hexes)
    targets = {_unit.pk: {} for _unit in game_instance.units.values() if _unit.position in target_hexes}
    for _unit_id in targets:
        damage = 5
        _unit = game_instance.units[_unit_id]
        unit_hex = game_instance.board.hexes.get(_unit.position)
        dq, dr = unit_hex['q'] - hero_hex['q'], unit_hex['r'] - hero_hex['r']
        hex_behind_id = f"{unit_hex['q'] + dq};{unit_hex['r'] + dr}"
        hex_behind = game_instance.board.hexes.get(hex_behind_id)
        if not hex_behind or hex_behind['occupied_by'] != 'empty':
            print('hex_behind', hex_behind)
            damage *= 2
        else:
            game_instance.board.hexes[_unit.position]['occupied_by'] = 'empty'
            _unit.position = hex_behind_id
            game_instance.board.place_game_object(_unit)
            _unit.moves = list(game_instance.board.get_hexes_in_range(hex_behind, _unit.move_range, ['empty']).keys())
            _unit.attack_hexes = list(
                game_instance.board.get_hexes_in_range(hex_behind, _unit.attack_range, ['empty', 'hero']).keys())
        targets[_unit_id]['damage'] = game_instance.damage_instance(game_instance.game.hero, _unit, damage)
    result['targets'] = targets
    print('target units', targets)
    return result
