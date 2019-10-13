from game.models import Hero, Item
from rest_framework import serializers


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
