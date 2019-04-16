from django.contrib import admin

from util.models import *


class EmailAgendadoAdmin(admin.ModelAdmin):
    list_display = ('subject', 'to', 'status', 'date')
    readonly_fields = ('subject', 'to', 'status', 'date')
    fields = ('subject', 'to', 'status', 'date', 'html')
    actions = ('renviar', )
    multi_search = (
        ('q1', 'Para', ['to']),
        ('q2', 'Assunto', ['subject']),
    )

    class Media:
        js = [
            'tiny_mce/tiny_mce.js',
            'tiny_mce/tiny_mce_settings.js',
        ]

    def renviar(self, request, queryset):
        for q in queryset:
            q.send_email()


admin.site.register(EmailAgendado, EmailAgendadoAdmin)
admin.site.register(UserToken)


