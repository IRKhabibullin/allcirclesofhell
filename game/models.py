from django.utils.timezone import now
from django.contrib.auth.models import User

from django.db import models


class HandbookModel(models.Model):
    """
    Model for storing sets of game objects, like list of existing spells, or bestiary.
    It should not store data for every game instance, it's common for all the games.
    """
    code_name = models.CharField(max_length=50, null=True)
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name

    # def save(self, *args, **kwargs):
    #     return


class EffectModel(HandbookModel):
    """Table listing all effects available in game"""
    description = models.TextField(default='Not provided')
    # trigger = models.?


class SkillModel(HandbookModel):
    """Table listing all skills available in game"""
    requirements = models.ManyToManyField('self', blank=True)
    effects = models.ManyToManyField(EffectModel, blank=True)
    description = models.TextField(default='Not provided')
    # school = models.IntegerField(default=0) it must be enum field
    img_path = models.TextField(default='./src/assets/skill.jpeg')


class ItemModel(HandbookModel):
    """Table listing all items available in game"""
    cost = models.IntegerField()
    effects = models.ManyToManyField(EffectModel, blank=True)
    description = models.TextField(default='Not provided')
    img_path = models.TextField(default='./src/assets/item.jpeg')


class ItemEffect(models.Model):
    """Intermediary table to bind spells and effects"""
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    effect = models.ForeignKey(Effect, on_delete=models.CASCADE)
    value = models.FloatField(default=0.0)

    def __str__(self):
        return f'{self.item.code_name}.{self.effect.code_name}'


class SpellModel(HandbookModel):
    """Table listing all spells available in game"""
    cost = models.IntegerField()
    effects = models.ManyToManyField(EffectModel, through='SpellEffectModel', through_fields=('spell', 'effect'), blank=True)
    description = models.TextField(default='Not provided')
    # school = models.IntegerField(default=0) it must be enum field
    img_path = models.TextField(default='./src/assets/spell.jpeg')


class SpellEffectModel(models.Model):
    """Intermediary table to bind spells and effects"""
    spell = models.ForeignKey(SpellModel, on_delete=models.CASCADE)
    effect = models.ForeignKey(EffectModel, on_delete=models.CASCADE)
    value = models.FloatField(default=0.0)

    def __str__(self):
        return f'{self.spell.code_name}.{self.effect.code_name}'


class GameStructure(HandbookModel):
    """Table listing game structures"""
    img_path = models.TextField(default='./src/assets/building.png')
    round_frequency = models.IntegerField(default=1)  # structure will appear every <round_frequency> rounds
    position = None
    assortment = []


class BaseUnitModel(models.Model):
    """Base model for units, heroes etc"""
    health = models.IntegerField(default=50)
    damage = models.IntegerField(default=3)
    attack_range = models.IntegerField(default=1)
    move_range = models.IntegerField(default=1)
    armor = models.IntegerField(default=2)
    skills = models.ManyToManyField(SkillModel, blank=True)
    spells = models.ManyToManyField(SpellModel, blank=True)
    img_path = models.TextField(default='')
    position = None
    moves = []
    attack_hexes = []

    class Meta:
        abstract = True


class UnitModel(HandbookModel, BaseUnitModel):
    """
    There could be several identical units in game, but none of them should be saved to db

    When creating unit for game instance, should be used dict/class with unit's attributes instead
    to avoid accidental save
    Also maybe I should override save method to do nothing if it is clear that someone trying to save it by mistake
    """
    level = models.IntegerField(default=1)
    img_path = models.TextField(default='./src/assets/unit.jpeg')


class HeroModel(BaseUnitModel):
    """Main character in game"""
    name = models.CharField(max_length=50)
    weapon = models.ForeignKey(ItemModel, on_delete=models.CASCADE, related_name='hero_weapon', null=True, blank=True)
    suit = models.ForeignKey(ItemModel, on_delete=models.CASCADE, related_name='hero_suit', null=True, blank=True)
    img_path = models.TextField(default='./src/assets/board_hero_sized.png')
    # school = models.IntegerField(default=0) it must be enum field

    def __str__(self):
        return self.name


class GameModel(models.Model):
    """Game data storing model"""
    created = models.DateTimeField(default=now)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    hero = models.ForeignKey(HeroModel, on_delete=models.CASCADE, null=True, blank=True)
    round = models.IntegerField(default=1)  # round in the game
    # jsoned state of game. Need to save board state, shops assortment and so on
    state = models.TextField(default='{}')
