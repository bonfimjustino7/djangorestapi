#coding: utf-8
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.http import JsonResponse

from django.conf import settings
from django.contrib import messages

from util.models import create_token, UserToken, valid_token

from .forms import *
from .models import *
from inscricao.models import EmpresaUsuario

# TODO: (Nova Empresa): Além dos 3 botões, deve-se habilitar um inline onde o usuário poderá preencher uma ou mais agências (os dados serão gravados em EmpresaAgencia). O inline só precisa conter o Nome e a UF. Deve existir uma crítica para não permitir que o Estado da Agência não esteja contido em Regional.estados.

################
#### Testes ####
################

def envia_email(remetente = '', destinatario = '', assunto = '', mensagem = ''):
    print(
        '\n\nE-mail:\n{} -> {}\n{}\n{}\n\n'.format(
            remetente,
            destinatario,
            assunto,
            mensagem,
        )
    )

#####################################
#### Fim das rotinas para testes ####
#####################################

class LoginView(View):
    template = 'base/login_bulma.html'
    dados = {}

    def get(self, request, **kwargs):
        if request.user.is_authenticated:
            return redirect('start')

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
                        return redirect('start')
                else:
                    messages.warning(request, 'Conta desabilitada. :(')
            else:
                messages.warning(request, 'Usuário ou senha incorretos. Tente novamente.')
        return render(request, self.template, self.dados)

class Registro1View(View):
    template = 'base/registro.html'
    dados = {}

    def get(self, request, **kwargs):
        self.dados['formulario_registro'] = Registro1Form()
        return render(request, self.template, self.dados)

    def post(self, request, **kwargs):
        self.dados['formulario_registro'] = Registro1Form(request.POST)
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

                # TODO: Incluir rotina para enviar o e-mail.
                envia_email('sistema', 'usuário', 'Cadastro em Colunistas', mensagem)

                messages.success(request, 'Verifique seu e-mail para completar o cadastro.')
            except:
                messages.error(request, 'Houve um erro ao cadastrar o usuário e enviar o e-mail.')
        return redirect('instrucoes-login')

class Registro2View(View):
    template = 'base/registro2.html'
    dados = {}

    def get(self, request, **kwargs):
        self.dados['formulario_registro'] = Registro2Form()
        if UserToken.objects.filter(token = self.kwargs['token']).exists():
            self.dados['token_usuario'] = self.kwargs['token']
        else:
            messages.error(request, 'Pré-cadastro não encontrado.')
        return render(request, self.template, self.dados)

    def post(self, request, **kwargs):
        self.dados['formulario_registro'] = Registro2Form(request.POST)

        if not request.POST.get('usuario'):
            self.dados['formulario_registro'].add_error('usuario', 'O campo usuário é obrigatório.')
        elif User.objects.filter(username = request.POST.get('usuario')).exists():
            self.dados['formulario_registro'].add_error('usuario', 'Esse nome de usuário já foi utilizado. Por favor, escolha outro.')

        if self.dados['formulario_registro'].is_valid():
            try:
                user = User.objects.get(
                    username = UserToken.objects.get(token = self.kwargs['token']).owner,
                )
                if valid_token(owner = user.username, tk = UserToken.objects.get(owner = user.username).token):
                    user.username = self.dados['formulario_registro'].cleaned_data['usuario']
                    user.set_password(self.dados['formulario_registro'].cleaned_data['senha'])
                    user.save()

                    messages.success(request, 'Usuário cadastrado com sucesso.')
                else:
                    messages.error(request, 'Token inválido ou desativado. Realize seu pré-cadastro novamente.')
                return redirect('start')
            except Exception as erro:
                messages.error(request, 'Erro: {}'.format(erro.__str__()))
        return render(request, self.template, self.dados)

class InstrucoesLoginView(View):
    template = 'base/instrucoes-login.html'
    dados = {}

    def get(self, request, **kwargs):
        return render(request, self.template, self.dados)

class ReiniciaSenha1View(View):
    template = 'base/reinicia-senha.html'
    dados = {}

    def get(self, request, **kwargs):
        self.dados['formulario'] = ResetSenhaForm()
        return render(request, self.template, self.dados)

    def post(self, request, **kwargs):
        self.dados['formulario'] = ResetSenhaForm(request.POST)
        if self.dados['formulario'].is_valid():
            try:
                if User.objects.filter(email = self.dados['formulario'].cleaned_data['email']).exists():
                    user = User.objects.get(email = self.dados['formulario'].cleaned_data['email'])
                    token_usuario = UserToken.objects.create(
                        owner = user.username,
                    )

                    mensagem = 'Olá {},\nFoi solicitado ao sistema modificar a sua senha no nosso site.\nPara realizar essa operação, clique no link abaixo ou copie o endereço em seu navegador:\n\n{}/nova-senha/{}/\n\nCaso você não tenha solicitado uma nova senha, desconsidere essa mensagem.\nAtenciosamente,\nEquipe Colunistas'.format(
                        user.first_name,
                        settings.SITE_HOST,
                        token_usuario.token,
                    )
                    # TODO: Incluir código para enviar o e-mail
                    envia_email('sistema', user.email, 'Recuperação de Senha', mensagem)

                    messages.success(request, 'Verifique seu e-mail para mudar a sua senha.')
                else:
                    messages.warning(request, 'Usuário não cadastrado.')
                    return render(request, self.template, self.dados)
            except Exception as erro:
                messages.error(request, 'Erro: {}'.format(erro.__str__()))
        return redirect('instrucoes-login')

class ReiniciaSenha2View(View):
    template = 'base/reinicia-senha2.html'
    dados = {}

    def get(self, request, **kwargs):
        if UserToken.objects.filter(token = self.kwargs['token']).exists():
            self.dados['formulario'] = Registro2Form()
            self.dados['formulario'].fields['usuario'].initial = UserToken.objects.get(token = self.kwargs['token']).owner
            self.dados['formulario'].fields['usuario'].widget.attrs['disabled'] = 'disabled'
            self.dados['token'] = self.kwargs['token']
        else:
            messages.error(request, 'Usuário não encontrado.')

        return render(request, self.template, self.dados)

    def post(self, request, **kwargs):
        if UserToken.objects.filter(token = self.kwargs['token']).exists():
            self.dados['formulario'] = Registro2Form(request.POST)
            self.dados['formulario'].fields['usuario'].initial = UserToken.objects.get(token = self.kwargs['token']).owner
            self.dados['formulario'].fields['usuario'].widget.attrs['disabled'] = 'disabled'

            if self.dados['formulario'].is_valid():
                try:
                    user = User.objects.get(username = UserToken.objects.get(token = self.kwargs['token']).owner)
                    if valid_token(owner = user.username, tk = self.kwargs['token']):
                        user.set_password(self.dados['formulario'].cleaned_data['senha'])
                        user.save()
                        messages.success(request, 'Senha alterada com sucesso. Faça o login para continuar.')
                        return redirect('login')
                    else:
                        messages.error(request, 'Token inválido.')
                except Exception as erro:
                    messages.error(request, 'Erro: {}'.format(erro.__str__()))
        return render(request, self.template, self.dados)

class InicioView(LoginRequiredMixin, View):
    template = 'base/base.html'
    dados = {}

    def get(self, request, **kwargs):
        return render(request, self.template, self.dados)

class NovaEmpresaView(LoginRequiredMixin, View):
    template = 'base/nova-empresa.html'
    dados = {}

    def get(self, request, **kwargs):
        self.dados['formulario_cadastro'] = RegistroEmpresaForm()
        self.dados['formulario_fiscal'] = DadosFiscaisEmpresaForm()
        return render(request, self.template, self.dados)

    def post(self, request, **kwargs):
        resposta = {}
        formulario = RegistroEmpresaForm(request.POST)

        if Empresa.objects.filter(nome = request.POST.get('nome')).exists():
            formulario.add_error('nome', 'Já existe uma empresa cadastrada com esse nome. Por favor, utilize outro.')

        if formulario.is_valid():
            try:
                empresa = formulario.save()

                EmpresaUsuario.objects.create(
                    empresa = empresa,
                    usuario = request.user.usuario_set.first(),
                )

                resposta['status'] = 200
            except Exception as erro:
                resposta['status'] = 500
                resposta['texto'] = 'Erro: {}'.format(erro.__str__())
        else:
            resposta['status'] = 500
            resposta['texto'] = 'Dados preenchidos incorretamente.'
        return JsonResponse(resposta)

def logoutview(request):
    logout(request)
    return redirect('login')

####################
#### Auxiliares ####
####################

def consulta_empresa(request, nome):
    resposta = {}
    if Empresa.objects.filter(nome__icontains = nome).exists():
        resposta['existe'] = True
    else:
        resposta['existe'] = False
    return JsonResponse(resposta)

def cadastro_fiscal(request): # TODO: Desenvolver cadastro
    resposta = {}
    if request.POST:
        formulario = DadosFiscaisEmpresaForm(request.POST)
        if formulario.is_valid():
            print('\n\nCNPJ: {}\nIE: {}\nIM: {}\n\n'.format(
                formulario.cleaned_data['cnpj'],
                formulario.cleaned_data['inscricao_estadual'],
                formulario.cleaned_data['inscricao_municipal'],
            ))
            resposta['status'] = 200
        else:
            resposta['status'] = 500
            resposta['texto'] = 'Dados incorretos. Por favor, tente novamente.'
    else:
        resposta['status'] = 500
        resposta['texto'] = 'Método de requisição inválido.'
    return JsonResponse(resposta)
