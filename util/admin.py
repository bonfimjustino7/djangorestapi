from django.contrib import admin, messages
from django.contrib.auth.models import Group, Permission

from django.contrib.auth.admin import GroupAdmin
from poweradmin.admin import PowerModelAdmin, PowerButton

from django import forms
from django.contrib import admin
from django.http import HttpResponse, HttpResponseRedirect

from django.core.urlresolvers import reverse
from django.conf.urls import url
from django.shortcuts import render


import json as simplejson

from util.models import *


class ImportGroupForm(forms.Form):
    json = forms.FileField(required=True)


class GroupAdminCustom(GroupAdmin, PowerModelAdmin):
    list_display = ('name', )
    actions = ('export_json', )

    def export_json(self, request, queryset):
        json = []
        for query in queryset:
            json_query = {
                'name': query.name,
            }
            permissions_json = []
            for perm in query.permissions.all():
                permissions_json.append({
                    'name': perm.name,
                    'codename': perm.codename,
                    'app_label': perm.content_type.app_label,
                    'model': perm.content_type.model,
                })
            json_query['permissions'] = permissions_json
            json.append(json_query)

        response = HttpResponse(simplejson.dumps(json, ensure_ascii=False), content_type='text/javascript; charset=utf-8', )
        response['Content-Disposition'] = 'attachment; filename=groups.json'
        return response
    export_json.short_description = u'Exportar JSON'

    def import_json(self, request, form_class=ImportGroupForm, template_name='admin/auth/group/import-json.html'):
        form = form_class()
        if request.method == 'POST':
            form = form_class(request.POST, request.FILES)
            if form.is_valid():
                json = simplejson.loads(form.cleaned_data['json'].read())

                for group_json in json:
                    group = Group.objects.get_or_create(name=group_json['name'])[0]
                    for perm_json in group_json['permissions']:
                        try:
                            content_type = ContentType.objects.get(
                                app_label=perm_json['app_label'],
                                model=perm_json['model']
                            )
                            perm = Permission.objects.get(
                                codename=perm_json['codename'],
                                content_type=content_type
                            )
                            group.permissions.add(perm)
                        except (Permission.DoesNotExist, ContentType.DoesNotExist):
                            messages.error(request, u'Permissão "%s" do Grupo "%s" não existe!' % (
                                    perm_json['name'],
                                    group_json['name'],
                                )
                            )
                    group.save()

                messages.info(request, u'%s Grupo(s) importado(s)!' % len(json))
                return HttpResponseRedirect(reverse('admin:auth_group_changelist'))

        return render(request, template_name, {
            'title': u'Importar JSON',
            'form': form,
        })

    def get_urls(self):
        urls = super(GroupAdminCustom, self).get_urls()
        return [
            url(r'^import/json/$', self.import_json, name='auth_group_import_json'),
        ] + urls

    def get_buttons(self, request, object_id):
        buttons = super(GroupAdminCustom, self).get_buttons(request, object_id)
        if not object_id:
            buttons.append(PowerButton(url=reverse('admin:auth_group_import_json'), label='Importar JSON') )
        return buttons


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

admin.site.unregister(Group)
admin.site.register(Group, GroupAdminCustom)


