from re import search
from django.contrib import admin
from .models import *

# Register your models here.

class AvatarAdmin(admin.ModelAdmin):
    search_fields = ['avatar_name']
    readonly_fields = ['creator']

class ItemAdmin(admin.ModelAdmin):
    search_fields = ['item_name']
    readonly_fields = ['creator','avatar']

admin.site.register(Creator)
admin.site.register(Avatar, AvatarAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(Customer, search_fields = ['user__username'])
admin.site.register(Folder)
admin.site.register(RelationQueue)