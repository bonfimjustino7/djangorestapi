from django.contrib import admin

from poweradmin.admin import PowerModelAdmin, PowerButton, PowerStackedInline, PowerTabularInline
from tabbed_admin import TabbedModelAdmin

from base.models import *
from inscricao.models import *


class AgenciaInline(admin.TabularInline):
    model = EmpresaAgencia
    fields = ('agencia', 'uf', )
    extra = 0


@admin.register(Empresa)
class EmpresaAdmin(PowerModelAdmin):
    list_filter = ('regional',)
    list_display = ('nome', 'uf', 'municipio')
    fields = (('nome', ),('cep', 'uf', 'municipio', 'endereco'))
    inlines = [AgenciaInline]


class MaterialInline(admin.TabularInline):
    model = Material
    fields = ('tipo', 'arquivo', 'url')


@admin.register(Inscricao)
class InscricaoAdmin(TabbedModelAdmin):
    list_filter = ('premio', )
    list_display = ('empresa', 'seq', 'titulo', 'categoria', 'cliente')

    tab_info = (
        (None, {'fields': ('empresa', 'titulo', 'categoria', 'cliente')}),
    )

    tab_materiais = (
        MaterialInline,
    )

    tab_ficha_agencia = (
        (None, {'fields': ('DiretorCriacao',)}),
    )

    tab_ficha_fornec = (
        (None, {'fields': ('ProdutoraFilme',)}),
    )

    tabs = [
        ('Informações Gerais', tab_info),
        ('Quantidade de Materiais', tab_materiais),
        ('Ficha Técnica Agência', tab_ficha_agencia),
        ('Ficha Técnica Fornecedores', tab_ficha_fornec),
    ]


admin.site.register(TipoMaterial)

