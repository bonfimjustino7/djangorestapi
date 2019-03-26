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
from django.urls import path

from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from django.conf import settings

from filebrowser.sites import site

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^admin/filebrowser/', site.urls),
    url(r'^admin_tools/', include('admin_tools.urls')),
    url(r'^', include('base.urls')),
]

if 'theme' in settings.INSTALLED_APPS:
    urlpatterns += [url(r'^', include('theme.urls')), ]

urlpatterns += [
    # CMS
    url(r'^', include('cms.urls')),
    url(r'^ckeditor/', include('ckeditor.urls')),
    url(r'^chaining/', include('smart_selects.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)