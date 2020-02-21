"""
This file was generated with the custommenu management command, it contains
the classes for the admin menu, you can customize this class as you want.

To activate your custom menu add the following to your settings.py::
    ADMIN_TOOLS_MENU = '{{app}}.menu.CustomMenu'
"""

from django.urls import reverse
from django.utils.text import capfirst
from admin_tools.menu import items, Menu
from admin_tools.menu.items import MenuItem

from base.models import Premiacao


class CustomAppList(items.AppList):

    def init_with_context(self, context):
        models = self._visible_models(context['request'])
        for model, perms in models:
            if not perms['change']:
                continue
            item = MenuItem(title=capfirst(model._meta.verbose_name_plural), url=self._get_admin_change_url(model, context))
            self.children.append(item)


class CustomMenu(Menu):

    def __init__(self, **kwargs):
        Menu.__init__(self, **kwargs)
        self.children += [
            items.MenuItem('Tela Inicial', reverse('admin:index')),
            items.MenuItem('Empresas',
                children=[
                    items.MenuItem('Nova Empresa', '/admin/inscricao/empresa/add'),
                    items.MenuItem('Empresas Cadastradas', '/admin/inscricao/empresa/')
                ]
            ),
            items.MenuItem('Inscricões',
                children=[
                    items.MenuItem('Nova Inscrição', '/admin/inscricao/inscricao/add'),
                    items.MenuItem('Inscrições Cadastradas', '/admin/inscricao/inscricao/'),
                ]
            ),
            items.MenuItem('Impressões',
                children=[
                    items.MenuItem('Formulário de Custos', '/fomulario_custos/'),
                    items.MenuItem('Inscrições Cadastradas', '/inscricoes_cadastradas/'),
                ]
            ),
            items.MenuItem('Informações',
                children = [items.MenuItem(premiacao, premiacao.url_nova_aba()) for premiacao in Premiacao.objects.all()]
            ),
            CustomAppList(
                u'Adminstração',
                models=('django.contrib.*', 'admin_tools.dashboard.models.DashboardPreferences',),
            ),
            items.MenuItem('Teste', '/', )
        ]
    def init_with_context(self, context):
        pass