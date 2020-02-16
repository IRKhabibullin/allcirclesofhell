from rest_framework.fields import DictField, ListField

from game.models import HeroModel, ItemModel, GameModel, UnitModel, SpellModel
from rest_framework import serializers
from django.contrib.auth.models import User


class ItemSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ItemModel
        fields = ['name', 'cost', 'effects', 'description', 'img_path']


class SpellSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = SpellModel
        fields = ['code_name', 'name', 'cost', 'effects', 'description', 'img_path']

    effects = serializers.SerializerMethodField('spell_effects')

    def spell_effects(self, spell):
        return {item.effect.code_name: item.value for item in spell.spelleffectmodel_set.all()}


class HeroSerializer(serializers.HyperlinkedModelSerializer):
    weapon = ItemSerializer(read_only=True)
    suit = ItemSerializer(read_only=True)
    spells = SpellSerializer(read_only=True, many=True)

    class Meta:
        model = HeroModel
        fields = ['name', 'health', 'damage', 'move_range', 'attack_range', 'armor', 'skills', 'spells', 'img_path',
                  'suit', 'weapon', 'position', 'moves', 'attack_hexes']

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


class GameInstanceSerializer(serializers.Serializer):
    board = serializers.SerializerMethodField('game_board')
    round = serializers.SerializerMethodField('game_round')
    hero = serializers.SerializerMethodField('game_hero')
    game_id = serializers.SerializerMethodField('game_pk')
    # game = GameSerializer(read_only=True)
    units = serializers.SerializerMethodField('game_units')

    def game_hero(self, game):
        hero = HeroSerializer(game.hero._object).data
        hero['position'] = game.hero.position.id
        return hero

    def game_units(self, game):
        units = {pk: UnitSerializer(unit._object).data for pk, unit in game.units.items()}
        for pk, unit in units.items():
            unit['position'] = game.units[pk].position.id
        return units

    def game_board(self, game):
        return game.board.get_state()

    def game_round(self, game):
        return game._game.round

    def game_pk(self, game):
        return game._game.pk
