"""colunistas URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
	https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
	1. Add an import:  from my_app import views
	2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
	1. Add an import:  from other_app.views import Home
	2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
	1. Import the include() function: from django.urls import include, path
	2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin

from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from django.conf import settings
from inscricao import views
from filebrowser.sites import site

# django 2
# from django.urls import path
# from django.conf.urls import include
# urlpatterns = [
# 	path('admin_tools/', include('admin_tools.urls')),
# 	path('', include('base.urls')),
# ]
from util.views import montar_nome

admin.site.site_header = settings.SITE_NAME


urlpatterns = [
	url(r'^admin/', admin.site.urls),
	url(r'^admin_tools/', include('admin_tools.urls')),
	url(r'^ckeditor/', include('ckeditor.urls')),
	url(r'^chaining/', include('smart_selects.urls')),
	url(r'^', include('base.urls')),
	url(r'^', include('util.urls')),
	url(r'^tipos_materiais/(?P<id>\d+)/$', views.tipo_materiais),
	url(r'^filtrar_estados/(?P<id>\d+)/$', views.filtrar_estados),
	url(r'^dica_material/(?P<id>\d+)/$', views.dica_materiais),
	url(r'^dica_material/name/(?P<name>\w+)/$', views.dica_materiais_by_name),
	url(r'^baixar_material/(?P<id>\d+)/$', montar_nome),
	url(r'^get_tipo_materiais/(?P<id>\d+)/$', views.get_tipo_materiais),
	url(r'^fomulario_custos/$', views.formularios_custos),
	url(r'^inscricoes_cadastradas/$', views.inscricoes_cadastradas),
	url(r'^admin/inscricao/finalizar/$', views.finalizar),
	url(r'^empresa_download/(?P<id>\d+)/$', views.empresa_download),
	url(r'^delete/(?P<pk>\w+)/$', views.delete_material),
	url(r'^salvar_material', views.salvar_material),
	url(r'^redirect', views.url_redirect),


]

if settings.LOCAL:
	urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
	urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if 'theme' in settings.INSTALLED_APPS:
	urlpatterns += [url(r'^/', include('theme.urls')), ]


