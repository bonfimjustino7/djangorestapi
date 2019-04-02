from django.contrib import admin

from base.models import *


class PremioInline(admin.TabularInline):
    model = Premio
    fields = ['ano', 'regional', 'status']
    ordering = ['-ano']
    extra = 0


@admin.register(Premiacao)
class PremiacaoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'codigo', 'ordem']
    list_editable = ['ordem']
    ordering = ['ordem']
    inlines = [PremioInline]


admin.site.register(Regional)
admin.site.register(Categoria)
admin.site.register(Atividade)
admin.site.register(UF)
