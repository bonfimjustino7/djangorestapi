# -*- coding: utf-8 -*-
from django.urls import path
from base.views import *

urlpatterns = [
    path('instrucoes-login/', InstrucoesLoginView.as_view(), name = 'instrucoes-login'),
    path('registro/', Registro1View.as_view(), name = 'registro'),
    path('novo-usuario/<str:token>/', Registro2View.as_view(), name = 'novo-usuario'),
    path('reset-senha/', ReiniciaSenha1View.as_view(), name = 'reset-senha'),
    path('nova-senha/<str:token>/', ReiniciaSenha2View.as_view(), name = 'nova-senha'),

    path('login/', LoginView.as_view(), name = 'login'),
    path('logout/', logoutview, name = 'logout'),

    path('start/', InicioView.as_view(), name = 'start'),
    path('nova-empresa/', NovaEmpresaView.as_view(), name = 'nova-empresa'),

    path('consulta-empresa/<str:nome>/', consulta_empresa, name = 'consulta-empresa'),
    path('estados-regional/', estados_regional, name = 'estados-regional'),
    path('cadastro-fiscal/', cadastro_fiscal, name = 'cadastro-fiscal'),
]
