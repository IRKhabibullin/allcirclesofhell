from game.models import Hero, Item, GameModel, Unit
from rest_framework import serializers
from django.contrib.auth.models import User


class ItemSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Item
        fields = ['name', 'cost', 'effects', 'description', 'img_path']


class HeroSerializer(serializers.HyperlinkedModelSerializer):
    weapon = ItemSerializer(read_only=True)
    suit = ItemSerializer(read_only=True)

    class Meta:
        model = Hero
        fields = ['name', 'health', 'damage', 'attack_range', 'armor', 'skills', 'spells', 'img_path', 'suit', 'weapon']


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
                  'move_range', 'position']


class GameInstanceSerializer(serializers.Serializer):
    board = serializers.SerializerMethodField('game_board')
    game = GameSerializer(read_only=True)
    units = UnitSerializer(many=True, read_only=True)

    def game_board(self, game):
        return game.board.get_state()
