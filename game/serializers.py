from rest_framework.fields import DictField, ListField

from game.models import HeroModel, ItemModel, GameModel, UnitModel, SpellModel, GameStructureModel, SkillModel
from rest_framework import serializers
from django.contrib.auth.models import User


class ItemSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ItemModel
        fields = ['name', 'cost', 'effects', 'description', 'img_path']

    effects = serializers.SerializerMethodField('item_effects')

    def item_effects(self, item):
        return {x.effect.code_name: x.value for x in item.itemeffectmodel_set.all()}


class SpellSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = SpellModel
        fields = ['code_name', 'name', 'cost', 'effects', 'description', 'img_path']

    effects = serializers.SerializerMethodField('spell_effects')

    def spell_effects(self, spell):
        return {item.effect.code_name: item.value for item in spell.spelleffectmodel_set.all()}


class SkillSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = SkillModel
        fields = ['code_name', 'name', 'cost', 'effects', 'description', 'img_path']

    effects = serializers.SerializerMethodField('skill_effects')

    def skill_effects(self, skill):
        return {item.effect.code_name: item.value for item in skill.skilleffectmodel_set.all()}


class HeroSerializer(serializers.HyperlinkedModelSerializer):
    weapon = ItemSerializer(read_only=True)
    suit = ItemSerializer(read_only=True)
    spells = SpellSerializer(read_only=True, many=True)
    skills = SkillSerializer(read_only=True, many=True)
    items = ItemSerializer(read_only=True, many=True)

    class Meta:
        model = HeroModel
        fields = ['name', 'health', 'damage', 'move_range', 'attack_range', 'armor', 'skills', 'spells', 'items',
                  'img_path', 'suit', 'weapon', 'position', 'moves', 'attack_hexes']

    # position = serializers.SerializerMethodField('hero_position')
    #
    # def hero_position(self, hero):
    #     print('hero in serializer', hero)
    #     print('hero position in serializer', hero.position)
    #     return f'{hero.position.q};{hero.position.r}'


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['username']


class GameSerializer(serializers.HyperlinkedModelSerializer):
    hero = HeroSerializer(read_only=True)

    class Meta:
        model = GameModel
        fields = ['pk', 'round', 'hero']


class UnitSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = UnitModel
        fields = ['pk', 'name', 'health', 'damage', 'attack_range', 'armor', 'skills', 'spells', 'img_path',
                  'move_range', 'position', 'moves', 'attack_hexes']

    # position = serializers.SerializerMethodField('unit_position')
    #
    # def unit_position(self, unit):
    #     return f'{unit.position.q};{unit.position.r}'


class StructureSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = GameStructureModel
        fields = ['pk', 'name', 'code_name', 'position', 'img_path']

    # position = serializers.SerializerMethodField('structure_position')
    #
    # def structure_position(self, structure):
    #     return f'{structure.position.q};{structure.position.r}'


class GameInstanceSerializer(serializers.Serializer):
    board = serializers.SerializerMethodField('game_board')
    round = serializers.SerializerMethodField('game_round')
    hero = serializers.SerializerMethodField('game_hero')
    game_id = serializers.SerializerMethodField('game_pk')
    # game = GameSerializer(read_only=True)
    units = serializers.SerializerMethodField('game_units')
    structures = serializers.SerializerMethodField('game_structures')

    def game_hero(self, game):
        hero = HeroSerializer(game.hero._object).data
        hero['position'] = game.hero.position.id
        return hero

    def game_units(self, game):
        units = {pk: UnitSerializer(unit._object).data for pk, unit in game.units.items()}
        for pk, unit in units.items():
            unit['position'] = game.units[pk].position.id
        return units

    def game_structures(self, game):
        structures = {pk: StructureSerializer(structure._object).data for pk, structure in game.structures.items()}
        for pk, structure in structures.items():
            structure['position'] = game.structures[pk].position.id
        return structures

    def game_board(self, game):
        return game._board.get_state()

    def game_round(self, game):
        return game._game.round

    def game_pk(self, game):
        return game._game.pk
