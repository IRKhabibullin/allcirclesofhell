"""
Functions for actions
"""
from game.models import BaseUnit


def move(game_instance, action_data: dict) -> dict:
    """Make hero move"""
    destination_hex = game_instance.board[action_data['destination']]
    if not destination_hex:
        return {'allowed': False}
    hero_hex = game_instance.board[game_instance.game.hero.position]
    if game_instance.board.distance(destination_hex, hero_hex) != 1:
        return {'allowed': False}
    if destination_hex.occupied_by != 'empty':
        return {'allowed': False}

    hero_hex.occupied_by = 'empty'
    game_instance.game.hero.position = f"{destination_hex.q};{destination_hex.r}"
    destination_hex.occupied_by = 'hero'
    return {'allowed': True}


def attack(game_instance, source: BaseUnit, target: BaseUnit) -> dict:
    """Simple melee attack"""
    hero_hex = game_instance.board[source.position]
    target_hex = game_instance.board[target.position]
    if game_instance.board.distance(hero_hex, target_hex) > source.attack_range:
        return {'allowed': False}
    damage_dealt = game_instance.damage_instance(source, target, source.damage)
    return {'allowed': True, 'damage': damage_dealt}


def range_attack(game_instance, source: BaseUnit, target: BaseUnit) -> dict:
    """Simple range attack"""
    hero_hex = game_instance.board[source.position]
    target_hex = game_instance.board[target.position]
    if game_instance.board.distance(hero_hex, target_hex) > source.attack_range + 1:
        return {'allowed': False}
    damage_dealt = game_instance.damage_instance(source, target, source.damage)
    return {'allowed': True, 'damage': damage_dealt}


def path_of_fire(game_instance, action_data: dict) -> dict:
    """Path of fire spell"""
    result = {'allowed': False}
    spell = game_instance.game.hero.spells.filter(name='Path of fire')
    start_hex = game_instance.board[action_data['target_hex']]
    hero_hex = game_instance.board[game_instance.game.hero.position]
    if not spell or not start_hex:
        return result
    spell_effects = {item.effect.code_name: item.value for item in spell[0].spelleffect_set.all()}
    if game_instance.board.distance(hero_hex, start_hex) > spell_effects['radius']:
        return result
    result['allowed'] = True
    dq, dr = start_hex.q - hero_hex.q, start_hex.r - hero_hex.r
    target_hexes, targets = [], []
    for i in range(1, int(spell_effects['path_length']) + 1):
        hex_id = f"{hero_hex.q + dq * i};{hero_hex.r + dr * i}"
        _hex = game_instance.board[hex_id, None]
        if not _hex or _hex.occupied_by == 'obstacle':
            break
        target_hexes.append(hex_id)
        if _hex.occupied_by == 'unit':
            targets.append(hex_id)
    targets = {_unit.pk: {} for _unit in game_instance.units.values() if _unit.position in targets}
    for _unit_id in targets:
        targets[_unit_id]['damage'] = game_instance.damage_instance(game_instance.game.hero,
                                                                    game_instance.units[_unit_id],
                                                                    spell_effects['damage'])
    result['targets'] = targets
    result['target_hexes'] = target_hexes
    return result


def shield_bash(game_instance, action_data: dict) -> dict:
    """Shield bash spell"""
    result = {'allowed': False}
    start_hex = game_instance.board[action_data['target_hex']]
    hero_hex = game_instance.board[game_instance.game.hero.position]
    if not start_hex or game_instance.board.distance(hero_hex, start_hex) != 1:
        return result
    result['allowed'] = True
    target_hexes = list(set(game_instance.board.get_hexes_in_range(start_hex, 1)).intersection(
        game_instance.board.get_hexes_in_range(hero_hex, 1)) - {game_instance.game.hero.position})
    targets = {_unit.pk: {} for _unit in game_instance.units.values() if _unit.position in target_hexes}
    for _unit_id in targets:
        damage = 5
        _unit = game_instance.units[_unit_id]
        unit_hex = game_instance.board[_unit.position]
        dq, dr = unit_hex.q - hero_hex.q, unit_hex.r - hero_hex.r
        hex_behind_id = f"{unit_hex.q + dq};{unit_hex.r + dr}"
        hex_behind = game_instance.board[hex_behind_id]
        if not hex_behind or hex_behind.occupied_by != 'empty':
            damage *= 2
        else:
            game_instance.board[_unit.position].occupied_by = 'empty'
            _unit.position = hex_behind_id
            game_instance.board.place_game_object(_unit)
            _unit.moves = list(game_instance.board.get_hexes_in_range(hex_behind, _unit.move_range, ['empty']).keys())
            _unit.attack_hexes = list(
                game_instance.board.get_hexes_in_range(hex_behind, _unit.attack_range, ['empty', 'hero']).keys())
        targets[_unit_id]['damage'] = game_instance.damage_instance(game_instance.game.hero, _unit, damage)
    result['targets'] = targets
    result['stunned_units'] = list(targets.keys())
    return result


def blink(game_instance, action_data: dict) -> dict:
    """Blink spell"""
    result = {'allowed': False}
    target_hex = game_instance.board[action_data['target_hex']]
    hero_hex = game_instance.board[game_instance.game.hero.position]
    if not target_hex or game_instance.board.distance(hero_hex, target_hex) > 3 or target_hex.occupied_by != 'empty':
        return result
    result['allowed'] = True
    hero_hex.occupied_by = 'empty'
    game_instance.game.hero.position = f"{target_hex.q};{target_hex.r}"
    target_hex.occupied_by = 'hero'
    return result
