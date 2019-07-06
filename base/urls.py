# -*- coding: utf-8 -*-
from django.conf.urls import url, include
from base.views import *

urlpatterns = [
    url(r'^$', HomeView.as_view(), name = 'home'),
    url('instrucoes-login/$', InstrucoesLoginView.as_view(), name = 'instrucoes-login'),
    url('instrucoes-reset-login/$', InstrucoesResetLoginView.as_view(), name = 'instrucoes-reset-login'),
    url('registro/$', Registro1View.as_view(), name = 'registro'),
    url('novo-usuario/(?P<token>[a-zA-Z0-9_.-]+)/$', Registro2View.as_view(), name = 'novo-usuario'),
    url('reset-senha/$', ReiniciaSenha1View.as_view(), name = 'reset-senha'),
    url('nova-senha/(?P<token>[a-zA-Z0-9_.-]+)/$', ReiniciaSenha2View.as_view(), name = 'nova-senha'),

    url('login/$', LoginView.as_view(), name = 'login'),
    url('logout/$', logoutview, name = 'logout'),

    url('start/$', InicioView.as_view(), name = 'start'),
    url('nova-empresa/$', NovaEmpresaView.as_view(), name = 'nova-empresa'),

    url('consulta-empresa/(?P<nome>[a-zA-Z0-9 ]+)/$', consulta_empresa, name = 'consulta-empresa'),
    url('estados-regional/$', estados_regional, name = 'estados-regional'),
    url('cadastro-fiscal/$', cadastro_fiscal, name = 'cadastro-fiscal'),
]
