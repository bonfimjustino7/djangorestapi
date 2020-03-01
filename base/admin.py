from django.contrib import admin
from django import forms

from inscricao.forms import PrecoForm
from smart_selects import form_fields

from poweradmin.admin import PowerModelAdmin, PowerTabularInline

from base.models import *




class PrecoInline(PowerTabularInline):
    model = Preco
    extra = 0
    form = PrecoForm

@admin.register(Premiacao)
class PremiacaoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'codigo', 'ordem']
    ordering = ['ordem']
    inlines = (PrecoInline,)


@admin.register(Categoria)
class CategoriaAdmin(PowerModelAdmin):
    list_filter = ('premiacao', )
    search_fields = ['codigo', 'nome']
    list_display = ['codigo', 'nome', 'descricao', ]
    ordering = ['codigo']


class PremioInlineFormSet(forms.models.BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super(PremioInlineFormSet, self).__init__(*args, **kwargs)
        self.initial_extra = [{'ano': ano_corrente()}, {'status': 'A'}]


class PremioRegionalInline(admin.TabularInline):
    model = Premio
    fields = ['ano', 'status', 'total_inscricoes', 'total_inscricoes_pendentes',]
    readonly_fields = ['total_inscricoes', 'total_inscricoes_pendentes',]
    ordering = ['-ano']
    extra = 0
    formset = PremioInlineFormSet


@admin.register(Regional)
class RegionalAdmin(PowerModelAdmin):
    inlines = [PremioRegionalInline]


@admin.register(TipoMaterial)
class TipoMaterialAdmin(PowerModelAdmin):
    fields = (('descricao', 'arquivo', 'url', 'youtube'), 'dicas')


class FormatoAdmin(PowerModelAdmin):
    list_filter = ('premiacao',)
    list_display = ('nome', 'codigo', 'premiacao')
    fields = ('nome', 'codigo', 'premiacao')


admin.site.register(UF)
admin.site.register(Area)
