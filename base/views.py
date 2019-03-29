#coding: utf-8
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.http import JsonResponse

from django.contrib import messages
from django.contrib.auth.models import *

from util.models import create_token, UserToken

from .forms import *
from .models import *

class LoginView(View):
    template = ''
    dados = {}

    def get(self, request, **kwargs):
        self.dados['formulario_login'] = LoginForm()
        if 'next' in request.GET:
            request.session['next'] = request.GET.get('next')
        return render(request, self.template, self.dados)

    def post(self, request, **kwargs):
        self.dados['formulario_login'] = LoginForm(request.POST)
        if self.dados['formulario_login'].is_valid():
            usuario = authenticate(
                username = self.dados['formulario_login'].cleaned_data['usuario'],
                password = self.dados['formulario_login'].cleaned_data['senha']
            )

            if usuario:
                if usuario.is_active:
                    login(request, usuario)

                    if 'next' in request.session:
                        retorno = request.session['next']
                        del request.session['next']
                        return redirect(retorno)
                    else:
                        return redirect('home')
                else:
                    messages.warning(request, 'Conta desabilitada. :(')
            else:
                messages.warning(request, 'Usuário ou senha incorretos. Tente novamente.')
        return render(request, self.template, self.dados)

class Registro1View(View):
    template = ''
    dados = {}

    def get(self, request, **kwargs):
        self.dados['formulario_registro'] = RegistroForm()
        return render(request, self.template, self.dados)

    def post(self, request, **kwargs):
        self.dados['formulario_registro'] = RegistroForm(request.POST)
        if self.dados['formulario_registro'].is_valid():
            try:

                user = User.objects.create(
                    username = create_token(10),
                    first_name = self.dados['formulario_registro'].cleaned_data['nome'],
                    last_name = self.dados['formulario_registro'].cleaned_data['sobrenome'],
                    email = self.dados['formulario_registro'].cleaned_data['email'],
                )

                token_usuario = UserToken.objects.create(owner = user.username)

                mensagem = 'Olá {},\nVocê demonstrou interesse em realizar o cadastro no site Colunistas.\nPara completar o seu cadastro, clique no link ou copie o endereço no seu navegador:\n{}\nAtenciosamente,\nEquipe Colunistas'.format(
                    self.dados['formulario_registro'].cleaned_data['nome'],
                    token_usuario.link(),
                )

                # TODO: Incluir rotina para enviar o e-mail

                messages.success(request, 'Verifique seu e-mail para completar o cadastro.')
            except:
                messages.error(request, 'Houve um erro ao cadastrar o usuário e enviar o e-mail.')
        return redirect('instrucoes-login')

class Registro2View(View):
    template = ''
    dados = {}

    def get(self, request, **kwargs):
        self.dados['formulario_registro'] = Registro2Form()
        if Usuario.objects.filter(token = self.kwargs['token']).exists():
            request.session['usuario'] = {
                'token': self.kwargs['token'],
            }
        else:
            messages.error(request, 'Pré-cadastro não encontrado.')
        return render(request, self.template, self.dados)

    def post(self, request, **kwargs):
        self.dados['formulario_registro'] = Registro2Form(request.POST)

        if User.objects.filter(username = request.POST.get('usuario')).exists():
            self.dados['formulario_registro'].add_error('usuario', 'Esse nome de usuário já foi utilizado. Por favor, escolha outro.')

        if self.dados['formulario_registro'].is_valid():
            try:
                user = User.objects.get(
                    username = UserToken.objects.get(token = request.session['token']).owner,
                )
                if valid_token(owner = user.username, tk = UserToken.objects.get(owner = user.username).token):
                    user.username = self.dados['formulario_registro'].cleaned_data['usuario']
                    user.set_password(self.dados['formulario_registro'].cleaned_data['senha'])
                    user.save()

                    del request.session['usuario']

                    messages.success(request, 'Usuário cadastrado com sucesso.')
                else:
                    messages.error(request, 'Token inválido ou desativado. Realize seu pré-cadastro novamente.')
            except:
                messages.error(request, 'Erro ao cadastrar o usuário.')
        return redirect('start')

class InstrucoesLoginView(View):
    template = ''
    dados = {}

    def get(self, request, **kwargs):
        return render(request, self.template, self.dados)

class ReiniciaSenha1View(View):
    template = ''
    dados = {}

    def get(self, request, **kwargs):
        self.dados['formulario'] = ResetSenhaForm()
        return render(request, self.template, self.dados)

    def post(self, request, **kwargs):
        self.dados['formulario'] = ResetSenhaForm(request.POST)
        if self.dados['formulario'].is_valid():
            try:
                user = User.objects.get(user__email = self.dados['formulario'].cleaned_data['email'])
                token_usuario = UserToken.objects.create(
                    owner = user.username,
                )

                mensagem = 'Olá {},\nFoi solicitado ao sistema modificar a sua senha no nosso site.\nPara realizar essa operação, clique no link abaixo ou copie o endereço em seu navegador:\n\n{}/nova-senha/{}/\n\nCaso você não tenha solicitado uma nova senha, desconsidere essa mensagem.\nAtenciosamente,\nEquipe Colunistas'.format(
                    user.first_name,
                    settings.SITE_HOST,
                    token_usuario.token,
                )
                # TODO: Incluir código para enviar o e-mail

                messages.success(request, 'Verifique seu e-mail para mudar a sua senha.')
            except:
                messages.error(request, 'Houve um erro ao processar seu pedido. Por favor, tente novamente.')
        return redirect('instrucoes-login')

class ReiniciaSenha2View(View):
    template = ''
    dados = {}

    def get(self, request, **kwargs):
        if UserToken.objects.filter(token = self.kwargs['token']).exists():
            self.dados['formulario'] = Registro2Form()
            self.dados['formulario'].fields['usuario'].required = False
            self.dados['formulario'].fields['usuario'].widget.attrs['disabled'] = 'disabled'

            request.session['token'] = self.kwargs['token']
        else:
            messages.error(request, 'Usuário não encontrado.')

        return render(request, self.template, self.dados)

    def post(self, request, **kwargs):
        if UserToken.objects.filter(token = self.kwargs['token']).exists():
            self.dados['formulario'] = Registro2Form(request.POST)

            if self.dados['formulario'].is_valid():
                try:
                    user = User.objects.get(username = UserToken.objects.get(token = self.kwargs['token']))
                    if valid_token(owner = user.username, tk = self.kwargs['token']):
                        user.set_password(self.dados['formulario'].cleaned_data['senha'])
                        messages.success(request, 'Senha alterada com sucesso.')
                    else:
                        messages.error(request, 'Token inválido.')
                except:
                    messages.error(request, 'Erro ao alterar a senha.')
        return render(request, self.template, self.dados)

class InicioView(LoginRequiredMixin, View):
    template = ''
    dados = {}

    def get(self, request, **kwargs):
        return render(request, self.template, self.dados)

class NovaEmpresaView(LoginRequiredMixin, View):
    template = ''
    dados = {}

    def get(self, request, **kwargs):
        self.dados['formulario_cadastro'] = RegistroEmpresaForm()
        return render(request, self.template, self.dados)

    def post(self, request, **kwargs):
        self.dados['formulario_cadastro'] = RegistroEmpresaForm(request.POST)

        if Empresa.objects.filter(nome = request.POST.get('nome')).exists():
            self.dados['formulario_cadastro'].add_error('nome', 'Já existe uma empresa cadastrada com esse nome. Por favor, utilize outro.')

        if self.dados['formulario_cadastro'].is_valid():
            try:
                empresa = self.dados['formulario_cadastro'].save()

                EmpresaUsuario.objects.create(
                    empresa = empresa,
                    usuario = request.user.usuario_set.first(),
                )

                messages.success(request, 'Empresa cadastrada com sucesso.')
            except Exception as erro:
                messages.error(request, 'Erro: {}'.format(erro.__str__()))
        return render(request, self.template, self.dados)

def logoutview(request):
    logout(request)

###################
#### Consultas ####
###################

def consulta_empresa(request, nome):
    resposta = {}
    if Empresa.objects.filter(nome__icontains = nome).exists():
        resposta['existe'] = True
    else:
        resposta['existe'] = False
    return JsonResponse(resposta)
