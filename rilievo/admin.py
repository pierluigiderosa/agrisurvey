# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.gis import admin
from .models import rilievo_poly,anagrafica

# Register your models here.
admin.site.register(rilievo_poly, admin.OSMGeoAdmin)


class anagraficaAdmin(admin.ModelAdmin):
    ordering = ["id"]


admin.site.register(anagrafica, anagraficaAdmin)