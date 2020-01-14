from django.contrib import admin
from django import forms
from poweradmin.admin import PowerModelAdmin

from base.models import *


@admin.register(Premiacao)
class PremiacaoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'codigo', 'ordem']
    ordering = ['ordem']


@admin.register(Categoria)
class CategoriaAdmin(PowerModelAdmin):
    list_filter = ('premiacao', )
    search_fields = ['codigo', 'nome']
    list_display = ['codigo', 'nome', 'descricao', ]
    ordering = ['codigo']


# TODO: Fazer funcionar
class PremioInlineFormSet(forms.models.BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super(PremioInlineFormSet, self).__init__(*args, **kwargs)
        self.initial_extra = [{'ano': '2019'}, {'status': 'A'}]


class PremioRegionalInline(admin.TabularInline):
    model = Premio
    fields = ['ano', 'status']
    ordering = ['-ano']
    extra = 0
    formset = PremioInlineFormSet


@admin.register(Regional)
class RegionalAdmin(PowerModelAdmin):
    inlines = [PremioRegionalInline]


@admin.register(TipoMaterial)
class TipoMaterialAdmin(PowerModelAdmin):
    fields = ('descricao', ('arquivo', 'url', 'roteiro'),)


class FormatoAdmin(PowerModelAdmin):
    list_filter = ('premiacao',)
    list_display = ('nome', 'codigo', 'premiacao')
    fields = ('nome', 'codigo', 'premiacao')


admin.site.register(UF)
admin.site.register(Area)
