from django.contrib import admin
from .models import Hero, Item, Spell, Effect, Skill, GameModel, Unit, SpellEffect, GameStructure


admin.site.register(GameModel)
admin.site.register(Hero)
admin.site.register(Item)
admin.site.register(Spell)
admin.site.register(SpellEffect)
admin.site.register(Effect)
admin.site.register(Skill)
admin.site.register(Unit)
admin.site.register(GameStructure)
