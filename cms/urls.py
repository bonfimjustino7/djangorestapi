# coding: utf-8
from django.conf.urls import url
from django.views.generic.base import RedirectView

from django.contrib.sitemaps.views import sitemap as sitemap_view

from cms.sitemap import sitemaps
from .views import *
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView

urlpatterns = [
    url(r'^update/$', UpdateView.as_view(), name='update'),

    url(r'^$', HomeView.as_view(), name='home'),
    url(r'^pesquisa/$', SearchView.as_view(), name='search'),
    url(r'^section/(?P<slug>[-_\w]+)/$', SectionDetailView.as_view(), name='section'),
    url(r'^download/(?P<file_uuid>[-_\w]+)/$', FileDownloadView.as_view(), name='download'),
    url(r'^link/a/(?P<article_slug>[-_\w]+)/$', LinkConversionView.as_view(), name='link'),
    url(r'^link/s/(?P<section_slug>[-_\w]+)/$', LinkConversionView.as_view(), name='link'),
    url(r'^sitemap\.xml$', sitemap_view, {'sitemaps': sitemaps}),
    url(r'^robots\.txt$', RobotsView.as_view(), name="robots"),

    url('login/', LoginView.as_view(template_name='auth/login.html'), name="cms_login"),
    url('logout/', LogoutView.as_view(template_name='auth/logout.html'), name='cms_logout'),
    url('password_change/', PasswordChangeView.as_view(template_name='auth/password_change_form.html'), name='cms_password_change'),
    url('password_change/done/', PasswordChangeDoneView.as_view(template_name='auth/password_change_done.html'),
         name='cms_password_change'),

    url(r'^signup/$', SignupView.as_view(), name='cms_signup'),
    url(r'^signup/filter/(?P<grouptype_id>[\d]+)/(?P<groupitem_id>[\d]+)/$', signup_filter, name='signup_filter'),
    url(r'^powerpost/$', RedirectView.as_view(url='/admin/cms/article/add-power/'), name="cms_article_powerpost"),

    url(r'^(?P<slug>[-_\w]+)/$', ArticleDetailView.as_view(), name='article'),
]