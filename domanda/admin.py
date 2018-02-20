# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.gis import admin
from .models import CatastaleSmall, danno,Agricoltore
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
# Register your models here.
admin.site.register(CatastaleSmall, admin.OSMGeoAdmin)


from .models import Agricoltore

class DannoAdmin(admin.ModelAdmin):
    list_display = ('author_full_name','id', 'richiedente','data_ins',)
    search_fields = ('foglio',)
    list_filter = ('data_ins',)
    ordering = ["-data_ins"]
    filter_horizontal = ('fog_part_certified',)

admin.site.register(danno,DannoAdmin)

class AgricoltoreAdmin(admin.ModelAdmin):
    list_display = ('user', 'CF','id', 'luogoNascita',)


admin.site.register(Agricoltore, AgricoltoreAdmin)
