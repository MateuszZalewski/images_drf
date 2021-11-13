from django.contrib import admin
from .models import Account, Tier, Perk

admin.site.register(Account)
admin.site.register(Tier)
admin.site.register(Perk)
