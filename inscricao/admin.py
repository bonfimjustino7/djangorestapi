from django.contrib import admin
from poweradmin.admin import PowerModelAdmin, PowerButton

from base.models import *
from inscricao.models import *


class AgenciaInline(admin.TabularInline):
    model = EmpresaAgencia
    fields = ['agencia', 'uf', ]
    extra = 0


@admin.register(Empresa)
class EmpresaAdmin(PowerModelAdmin):
    list_filter = ['regional',]
    list_display = ['nome', 'uf', 'municipio']
    ordering = ['nome']
    inlines = [AgenciaInline]


@admin.register(Inscricao)
class InscricaoAdmin(PowerModelAdmin):
    list_filter = ['empresa__regional', 'premio']
    list_display = ['empresa', 'seq', 'titulo', 'categoria', 'cliente']
    ordering = ['empresa', 'seq']


admin.site.register(TipoMaterial)

