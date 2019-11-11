from django.utils.timezone import now
from django.contrib.auth.models import User

from django.db import models
from .mechanics.board import Board

'''
All tables except Hero and GameInstance are for entity templates.
They shouldn't store entity instances.
There should be only one certain skill, effect, or item
And there could be many of game instances and heroes for them

There could be several identical units in game, but none of them should be saved to db
'''


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


class Unit(models.Model):
    """
    There could be several identical units in game, but none of them should be saved to db

    When creating unit for game instance, should be used dict/class with unit's attributes instead
    to avoid accidental save
    Also maybe I should override save method to do nothing if it is clear that someone trying to save it by mistake
    """
    name = models.CharField(max_length=50)
    level = models.IntegerField(default=1)
    health = models.IntegerField(default=50)
    damage = models.IntegerField(default=3)
    attack_range = models.IntegerField(default=1)
    move_range = models.IntegerField(default=1)
    armor = models.IntegerField(default=2)
    skills = models.ManyToManyField(Skill, blank=True)
    spells = models.ManyToManyField(Spell, blank=True)
    img_path = models.TextField(default='./src/assets/unit.jpeg')

    def get_new(self):
        pass

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
    # school = models.IntegerField(default=0) it must be enum field
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
        self.units = {}

    def init_board(self):
        if not self.board:
            if self.state != '{}':
                # from self.state
                pass
            else:
                self.board = Board(6)

    # def save_state(self):

    # def save(self, *args, **kwargs):
    #     self.save_state()
    #     super(GameInstance, self).save(*args, **kwargs)
