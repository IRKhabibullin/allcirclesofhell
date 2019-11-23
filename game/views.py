from django.contrib.auth.models import User

from game.models import Hero
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from game.serializers import HeroSerializer, UserSerializer, GameInstanceSerializer
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
    permission_classes = (IsAuthenticated,)
    gm = GameManager.instance()
    serializer_class = GameInstanceSerializer

    @action(detail=False)
    def list_by_user(self, request):
        """
        List games, created by current user.
        Pass auth token to query's header to define required user
        :param request:
        :return:
        """
        user_games = self.gm.get_games_by_user(request.user)
        games_info = [{
            'game_id': _game.pk,
            'created': _game.created.strftime('%d %b %y %H:%M'),
            'hero_name': _game.hero.name,
            'hero_hp': _game.hero.health,
            'round': _game.round
        } for _game in user_games]
        return Response(games_info)

    @action(detail=False, methods=['post'])
    def close_game(self, request, pk=None):
        # need to pass not game_id but uuid. It removes bug, when same game initialized in two browser tabs
        # also need to handle case when browser tab is closed
        """
        Removes initialized game_instance from game_manager
        :param request:
        :return:
        """
        removed = str(request.data['game_id']) in self.gm.game_instances
        if removed:
            del self.gm.game_instances[str(request.data['game_id'])]
        return Response({'removed': removed})

    def create(self, request):
        game_instance = self.gm.new_game(request.data.user_id)
        serializer = GameInstanceSerializer(game_instance)
        return Response(serializer.data)

    def destroy(self, request):
        pass

    def update(self, request):
        pass

    def retrieve(self, request, pk=None):
        game_instance = self.gm.get_game(str(pk))
        game_instance.init_round()
        serializer = GameInstanceSerializer(game_instance)
        return Response(serializer.data)


class GameAction(APIView):
    permission_classes = (IsAuthenticated,)
    gm = GameManager.instance()

    def post(self, request):
        """
        Handle actions
        """
        response_data = {'action': request.data['action']}
        if request.data['action'] == 'move':
            game_instance = self.gm.get_game(str(request.data['game_id']))
            response_data['allowed'] = game_instance.make_move(request.data['destination'])
            response_data.update(GameInstanceSerializer(game_instance).data)
        return Response(response_data)
