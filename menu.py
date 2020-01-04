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
            items.Bookmarks(u'Favoritos'),
            CustomAppList(
                u'Inscrição',
                models=('inscricao.models.*', )
            ),
            CustomAppList(
                u'Adminstração',
                models=('django.contrib.*', 'admin_tools.dashboard.models.DashboardPreferences', ),
            ),
        ]

