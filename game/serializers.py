from rest_framework.fields import DictField, ListField

from game.models import Hero, Item, GameModel, Unit, Spell
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


class GameInstanceSerializer(serializers.Serializer):
    board = serializers.SerializerMethodField('game_board')
    game = GameSerializer(read_only=True)
    units = DictField(child=UnitSerializer())

    def game_board(self, game):
        return game.board.get_state()
