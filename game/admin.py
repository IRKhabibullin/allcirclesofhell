from django.contrib import admin
from .models import Hero, Item, Spell, Effect, Skill, GameInstance


admin.site.register(GameInstance)
admin.site.register(Hero)
admin.site.register(Item)
admin.site.register(Spell)
admin.site.register(Effect)
admin.site.register(Skill)
