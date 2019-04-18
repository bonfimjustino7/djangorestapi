from django.contrib import admin
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
    list_display = ['codigo', 'nome', 'descricao', 'grupo']
    ordering = ['codigo']


admin.site.register(Regional)
admin.site.register(Atividade)
admin.site.register(UF)
