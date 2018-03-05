# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from ajax_select.admin import AjaxSelectAdmin
from django.contrib.gis import admin
from ajax_select import make_ajax_form
from .models import CatastaleSmall, danno, Agricoltore,catastale_new

# Register your models here.
admin.site.register(CatastaleSmall, admin.OSMGeoAdmin)
admin.site.register(catastale_new, admin.OSMGeoAdmin)

from .models import Agricoltore

class DannoAdmin(admin.ModelAdmin):
    list_display = ('author_full_name','id', 'richiedente','data_ins',)
    search_fields = ('foglio',)
    list_filter = ('data_ins',)
    ordering = ["-data_ins"]
    filter_horizontal = ('fog_part_certified',)

#uso AjaxSelectAdmin
#admin.site.register(danno,DannoAdmin)

@admin.register(danno)
class DannoAdminAjax(AjaxSelectAdmin):
    list_display = ('author_full_name', 'id', 'richiedente', 'data_ins',)
    search_fields = ('foglio',)
    list_filter = ('data_ins',)
    ordering = ["-data_ins"]
    filter_horizontal = ('fog_part_certified',)
    form = make_ajax_form(danno, {
        # fieldname: channel_name
        'fog_part_db': 'catastali'
    })


class AgricoltoreAdmin(admin.ModelAdmin):
    list_display = ('user', 'CF','id', 'luogoNascita',)


admin.site.register(Agricoltore, AgricoltoreAdmin)



