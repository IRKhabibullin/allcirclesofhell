from django.contrib import admin
from .models import HeroModel, ItemModel, SpellModel, EffectModel, SkillModel, GameModel, UnitModel, SpellEffectModel, GameStructureModel


admin.site.register(GameModel)
admin.site.register(HeroModel)
admin.site.register(ItemModel)
admin.site.register(SpellModel)
admin.site.register(SpellEffectModel)
admin.site.register(EffectModel)
admin.site.register(SkillModel)
admin.site.register(UnitModel)
admin.site.register(GameStructureModel)
