from django.db import models


class Effect(models.Model):
    name = models.CharField(max_length=50)
    effects = models.TextField()
    description = models.TextField(default='Not provided')
    # trigger = models.?


class Skill(models.Model):
    name = models.CharField(max_length=50)
    requirements = models.ManyToManyField('self')
    effects = models.ManyToManyField(Effect)
    description = models.TextField(default='Not provided')
    img_path = models.TextField(default='./src/assets/skill.jpeg')


class Item(models.Model):
    name = models.CharField(max_length=50)
    cost = models.IntegerField()
    effects = models.ManyToManyField(Effect)
    description = models.TextField(default='Not provided')
    img_path = models.TextField(default='./src/assets/item.jpeg')


class Spell(models.Model):
    name = models.CharField(max_length=50)
    cost = models.IntegerField()
    effects = models.ManyToManyField(Effect)
    description = models.TextField(default='Not provided')
    img_path = models.TextField(default='./src/assets/spell.jpeg')


class Hero(models.Model):
    name = models.CharField(max_length=50)
    health = models.IntegerField(default=50)
    damage = models.IntegerField(default=3)
    attack_range = models.IntegerField(default=1)
    armor = models.IntegerField(default=2)
    weapon = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='hero_weapon', null=True)
    suit = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='hero_suit', null=True)
    skills = models.ManyToManyField(Skill)
    spells = models.ManyToManyField(Spell)
    img_path = models.TextField(default='./src/assets/hero.jpeg')
