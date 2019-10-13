from django.shortcuts import render
from game.models import Hero
from rest_framework import viewsets
from game.serializers import HeroSerializer


class HeroViewSet(viewsets.ModelViewSet):
    queryset = Hero.objects.all()
    serializer_class = HeroSerializer


def home(request):
    return render(request, 'game/base.html')
