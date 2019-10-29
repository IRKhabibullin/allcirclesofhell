from django.contrib.auth.models import User
from game.models import Hero
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from game.serializers import HeroSerializer, UserSerializer, GameSerializer
from .mechanics.game_manager import GameManager


class HeroViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Hero.objects.all()
    serializer_class = HeroSerializer


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = User.objects.all()
    serializer_class = UserSerializer


class GameViewSet(viewsets.ViewSet):
    gm = GameManager()
    serializer_class = GameSerializer

    # def get_queryset(self):
    #     """
    #     This view should return a list of all the purchases
    #     for the currently authenticated user.
    #     """
    #     user = self.request.user
    #     print('passed user_id', self.request.query_params.get('user_id', None))
    #     print('action:', self.action)
    #     print('suffix:', self.suffix)
    #     print('name:', self.name)
    #     print('detail:', self.detail)
    #     return self.gm.get_games_by_user(user)

    @action(detail=False)
    def list_by_user(self, request):
        """
        List games, created by current user.
        Pass auth token to query's header to define required user
        :param request:
        :return:
        """
        user_games = self.gm.get_games_by_user(request.user)
        games_info = {_game.pk: {
            'created': _game.created,
            'hero_name': _game.hero.name,
            'hero_hp': _game.hero.health,
            'round': _game.round
        } for _game in user_games}
        return Response(games_info)

    def create(self, request):
        game_instance = self.gm.new_game(request.data.user_id)
        serializer = GameSerializer(game_instance)
        return Response(serializer.data)

    def destroy(self, request):
        pass

    def update(self, request):
        pass

    def retrieve(self, request, pk=None):
        game_instance = self.gm.get_game(pk)
        serializer = GameSerializer(game_instance)
        return Response(serializer.data)
