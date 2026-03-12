from django.contrib import admin
from .models import Region, Provincia, Ciudad


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'created_at')
    search_fields = ('nombre',)
    ordering = ('nombre',)


@admin.register(Provincia)
class ProvinciaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'region', 'created_at')
    search_fields = ('nombre', 'region__nombre')
    list_filter = ('region',)
    ordering = ('nombre',)


@admin.register(Ciudad)
class CiudadAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'provincia', 'created_at')
    search_fields = ('nombre', 'provincia__nombre')
    list_filter = ('provincia',)
    ordering = ('nombre',)
