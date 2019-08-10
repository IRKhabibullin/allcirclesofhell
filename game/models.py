from django.db import models


class Effect(models.Model):
    name = models.CharField(max_length=50)
    effects = models.TextField()


class Skill(models.Model):
    name = models.CharField(max_length=50)
    requirements = models.ManyToManyField('self')
    effects = models.ManyToManyField(Effect)


class Item(models.Model):
    name = models.CharField(max_length=50)
    limb = models.IntegerField()
    cost = models.IntegerField()
    effects = models.ManyToManyField(Effect)


class Spell(models.Model):
    name = models.CharField(max_length=50)
    cost = models.IntegerField()
    effects = models.ManyToManyField(Effect)


class Hero(models.Model):
    name = models.CharField(max_length=50)
    strength = models.IntegerField(default=5)  # hp per point: 20; damage per point: 3
    knowledge = models.IntegerField(default=5)  # manapool per point: 10; spellpower pre point: 1
    leadership = models.IntegerField(default=1)  # units per point: 1; level of units per point: 1
    skills = models.ManyToManyField(Skill)
    items = models.ManyToManyField(Item)  # (must be restrictions on items for same limb)
    spells = models.ManyToManyField(Spell)
