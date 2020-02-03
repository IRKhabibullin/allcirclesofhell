from rest_framework.fields import DictField, ListField

from game.models import Hero, Item, GameModel, Unit, Spell, GameStructure
from rest_framework import serializers
from django.contrib.auth.models import User


class ItemSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Item
        fields = ['name', 'cost', 'effects', 'description', 'img_path']


class SpellSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Spell
        fields = ['code_name', 'name', 'cost', 'effects', 'description', 'img_path']

    effects = serializers.SerializerMethodField('spell_effects')

    def spell_effects(self, spell):
        return {item.effect.code_name: item.value for item in spell.spelleffect_set.all()}


class HeroSerializer(serializers.HyperlinkedModelSerializer):
    weapon = ItemSerializer(read_only=True)
    suit = ItemSerializer(read_only=True)
    spells = SpellSerializer(read_only=True, many=True)

    class Meta:
        model = Hero
        fields = ['name', 'health', 'damage', 'move_range', 'attack_range', 'armor', 'skills', 'spells', 'img_path',
                  'suit', 'weapon', 'position', 'moves', 'attack_hexes']

    position = serializers.SerializerMethodField('hero_position')

    def hero_position(self, hero):
        return f'{hero.position.q};{hero.position.r}'


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
        model = Unit
        fields = ['pk', 'name', 'health', 'damage', 'attack_range', 'armor', 'skills', 'spells', 'img_path',
                  'move_range', 'position', 'moves', 'attack_hexes']

    position = serializers.SerializerMethodField('unit_position')

    def unit_position(self, unit):
        return f'{unit.position.q};{unit.position.r}'


class StructureSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = GameStructure
        fields = ['pk', 'name', 'code_name', 'position', 'img_path']

    position = serializers.SerializerMethodField('structure_position')

    def structure_position(self, structure):
        return f'{structure.position.q};{structure.position.r}'


class GameInstanceSerializer(serializers.Serializer):
    game_id = serializers.SerializerMethodField('game_pk')
    board = serializers.SerializerMethodField('game_board')
    round = serializers.SerializerMethodField('game_round')
    hero = HeroSerializer()
    units = DictField(child=UnitSerializer())
    structures = DictField(child=StructureSerializer())

    def game_board(self, game):
        return game.board.get_state()

    def game_round(self, game):
        return game._game.round

    def game_pk(self, game):
        return game._game.pk
