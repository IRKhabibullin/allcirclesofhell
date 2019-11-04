from django.utils.timezone import now
from django.contrib.auth.models import User

from django.db import models
from .mechanics.board import Board


class Effect(models.Model):
    name = models.CharField(max_length=50)
    effects = models.TextField()
    description = models.TextField(default='Not provided')
    # trigger = models.?

    def __str__(self):
        return self.name


class Skill(models.Model):
    name = models.CharField(max_length=50)
    requirements = models.ManyToManyField('self', blank=True)
    effects = models.ManyToManyField(Effect, blank=True)
    description = models.TextField(default='Not provided')
    img_path = models.TextField(default='./src/assets/skill.jpeg')

    def __str__(self):
        return self.name


class Item(models.Model):
    name = models.CharField(max_length=50)
    cost = models.IntegerField()
    effects = models.ManyToManyField(Effect, blank=True)
    description = models.TextField(default='Not provided')
    img_path = models.TextField(default='./src/assets/item.jpeg')

    def __str__(self):
        return self.name


class Spell(models.Model):
    name = models.CharField(max_length=50)
    cost = models.IntegerField()
    effects = models.ManyToManyField(Effect, blank=True)
    description = models.TextField(default='Not provided')
    img_path = models.TextField(default='./src/assets/spell.jpeg')

    def __str__(self):
        return self.name


class Hero(models.Model):
    name = models.CharField(max_length=50)
    health = models.IntegerField(default=50)
    damage = models.IntegerField(default=3)
    attack_range = models.IntegerField(default=1)
    armor = models.IntegerField(default=2)
    weapon = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='hero_weapon', null=True, blank=True)
    suit = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='hero_suit', null=True, blank=True)
    skills = models.ManyToManyField(Skill, blank=True)
    spells = models.ManyToManyField(Spell, blank=True)
    img_path = models.TextField(default='./src/assets/hero.jpeg')

    def __str__(self):
        return self.name


class GameInstance(models.Model):
    created = models.DateTimeField(default=now)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    hero = models.ForeignKey(Hero, on_delete=models.CASCADE, null=True, blank=True)
    round = models.IntegerField(default=1)  # round in the game
    # jsoned state of game. Need to save board state, shops assortment and so on
    state = models.TextField(default='{}')

    def __init__(self, *args, **kwargs):
        super(GameInstance, self).__init__(*args, **kwargs)
        self.board = None

    def init_board(self):
        if not self.board:
            if self.state != '{}':
                # from self.state
                pass
            else:
                self.board = Board(9, 11)

    # def save_state(self):

    # def save(self, *args, **kwargs):
