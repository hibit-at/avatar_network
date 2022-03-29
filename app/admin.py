from django.contrib import admin
from .models import *

# Register your models here.

class AvatarAdmin(admin.ModelAdmin):
    search_fields = ['avatar_name']

admin.site.register(Creator)
admin.site.register(Avatar, AvatarAdmin)
admin.site.register(Item)
admin.site.register(Customer)
admin.site.register(Folder)