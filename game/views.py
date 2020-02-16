from django.contrib.auth.models import User

from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from game.serializers import UserSerializer, GameInstanceSerializer
from .mechanics.actions import ActionResponse
from .mechanics.game_manager import GameManager


class UserViewSet(viewsets.ModelViewSet):
    """Viewset for users"""
    permission_classes = (IsAuthenticated,)
    queryset = User.objects.all()
    serializer_class = UserSerializer


class GameViewSet(viewsets.ViewSet):
    """Viewset for managing game instances"""
    permission_classes = (IsAuthenticated,)
    gm = GameManager.instance()
    serializer_class = GameInstanceSerializer

    @action(detail=False)
    def list_by_user(self, request):
        """List games, created by current user.
        Pass auth token to query's header to define required user"""
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
        """Removes initialized game_instance from game_manager"""
        # need to pass not game_id but uuid. It removes bug, when same game initialized in two browser tabs
        # also need to handle case when browser tab is closed
        removed = str(request.data['game_id']) in self.gm.game_instances
        if removed:
            del self.gm.game_instances[str(request.data['game_id'])]
        return Response({'removed': removed})

    def create(self, request):
        """Create new game for current user"""
        game_instance = self.gm.new_game(request.user, request.data['hero'])
        game_instance.init_round()
        serializer = GameInstanceSerializer(game_instance)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """Get game by given id"""
        game_instance = self.gm.get_game(str(pk))
        game_instance.init_round()
        serializer = GameInstanceSerializer(game_instance)
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        """Delete game by given id"""
        print(f'deleting game {pk}')
        deleted = self.gm.delete_game(str(pk))
        return Response({'deleted': deleted})


class GameAction(APIView):
    """
    View for game actions, like moving, attacking, using spells etc
    """
    permission_classes = (IsAuthenticated,)
    gm = GameManager.instance()

    def post(self, request):
        """
        Handle actions
        """
        print('request data', request.data)
        game_instance = self.gm.get_game(str(request.data['game_id']))
        action_response: ActionResponse = game_instance.make_turn(request.data)
        # action_data = {'action': request.data['action'], **game_instance.hero_action(request.data)}
        # if action_data['allowed']:
        #     response_data = GameInstanceSerializer(game_instance).data
        #     units_actions = action_data.pop('units_actions', [])
        #     for u_action in units_actions:
        #         response_data['units'][u_action['source']]['action'] = 'attack'
        #         response_data['units'][u_action['source']]['damage_dealt'] = u_action['damage_dealt']
        response_data = {**GameInstanceSerializer(game_instance).data, 'action_data': action_response.to_dict()}
        return Response(response_data)
