# -*- coding: utf-8 -*-
"""
This file was generated with the customdashboard management command, it
contains the two classes for the main dashboard and app index dashboard.
You can customize these classes as you want.

To activate your index dashboard add the following to your settings.py::
    ADMIN_TOOLS_INDEX_DASHBOARD = 'radix.dashboard.CustomIndexDashboard'

And to activate the app index dashboard::
    ADMIN_TOOLS_APP_INDEX_DASHBOARD = 'radix.dashboard.CustomAppIndexDashboard'
"""

from django.utils.translation import ugettext_lazy as _
from django.urls import reverse

from admin_tools.dashboard import modules, Dashboard, AppIndexDashboard
from admin_tools.utils import get_admin_site_name


class CustomIndexDashboard(Dashboard):
    """
    Custom index dashboard for radix.
    """
    columns = 2

    def init_with_context(self, context):
        site_name = get_admin_site_name(context)
        request = context.get('request')

        self.children += [
            modules.ModelList(
                u'Tabelas de Apoio',
                models=('base.*',)
            ),
            modules.ModelList(
                u'CMS',
                models=(
                    'cms.models.Article', 'cms.models.Section', 'cms.models.Menu',
                    'cms.models.FileDownload', 'cms.models.URLMigrate', 'cms.models.GroupType'
                ),
                exclude=('cms.models.EmailAgendado', 'cms.models.Theme', 'cms.models.Recurso', 'cms.models.'),
                extra=[
                    {'title': u'Visualizador de Arquivos', 'add_url': reverse('filebrowser:fb_upload'), 'change_url': reverse('filebrowser:fb_browse')},
                ]
            ),
            modules.ModelList(
                u'Adminstração',
                models=('django.contrib.*', 'admin_tools.dashboard.models.DashboardPreferences',  'core.models.PagSeguroRetorno', ),
            ),
            modules.ModelList(
                u'Parâmetros do Sistema',
                models=(
                    'cms.models.Recurso', 'cms.models.EmailAgendado', 'cms.models.Theme',
                ),
            ),
        ]


class CustomAppIndexDashboard(AppIndexDashboard):

    # we disable title because its redundant with the model list module
    title = ''

    def __init__(self, *args, **kwargs):
        AppIndexDashboard.__init__(self, *args, **kwargs)

        # append a model list module and a recent actions module
        self.children += [
            modules.ModelList(self.app_title, self.models),
            modules.RecentActions(
                _('Recent Actions'),
                include_list=self.get_app_content_types(),
                limit=5
            )
        ]

    def init_with_context(self, context):
        """
        Use this method if you need to access the request context.
        """
        return super(CustomAppIndexDashboard, self).init_with_context(context)
