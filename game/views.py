from django.shortcuts import render
from game.models import Hero
from rest_framework import viewsets
from rest_framework.response import Response
from game.serializers import HeroSerializer
from .mechanics.game_manager import GameManager


class HeroViewSet(viewsets.ModelViewSet):
    queryset = Hero.objects.all()
    serializer_class = HeroSerializer


class GameViewSet(viewsets.ViewSet):
    def create(self, request):
        gm = GameManager()
        game_instance = gm.new_game()
        return Response({'game_id': game_instance.pk})

    def destroy(self, request):
        pass

    def update(self, request):
        pass

    def retrieve(self, request):
        pass


def home(request):
    return render(request, 'game/base.html')


def new_game(request):
    gm = GameManager()
    game_instance = gm.new_game()
    # need to observe django custom api methods
    return {'game_id': game_instance.pk, 'battlefield': game_instance.battlefield.hexes}