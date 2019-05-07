from django.contrib import admin
from django import forms
from poweradmin.admin import PowerModelAdmin

from base.models import *


class PremioInline(admin.TabularInline):
    model = Premio
    fields = ['ano', 'regional', 'status']
    ordering = ['-ano']
    extra = 0


@admin.register(Premiacao)
class PremiacaoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'codigo', 'ordem']
    ordering = ['ordem']
    inlines = [PremioInline]


@admin.register(Categoria)
class CategoriaAdmin(PowerModelAdmin):
    search_fields = ['codigo', 'nome']
    list_display = ['codigo', 'nome', 'descricao', 'grupo']
    ordering = ['codigo']


# TODO: Fazer funcionar
class PremioInlineFormSet(forms.models.BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super(PremioInlineFormSet, self).__init__(*args, **kwargs)
        self.initial_extra = [{'ano': '2019'}, {'status': 'A'}]


class PremioRegionalInline(admin.TabularInline):
    model = Premio
    fields = ['ano', 'premiacao', 'status']
    ordering = ['-ano']
    extra = 0
    formset = PremioInlineFormSet


@admin.register(Regional)
class RegionalAdmin(PowerModelAdmin):
    inlines = [PremioRegionalInline]


@admin.register(TipoMaterial)
class TipoMaterialAdmin(PowerModelAdmin):
    fields = ('descricao', ('arquivo', 'url', 'roteiro'),)


admin.site.register(UF)
admin.site.register(Formato)
admin.site.register(Area)
