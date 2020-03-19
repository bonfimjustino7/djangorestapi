from collections import OrderedDict
from genericpath import exists
from ntpath import exists
from os.path import exists

from django.contrib import messages
#HEAD
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group, User
from django.forms import formset_factory
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils.safestring import mark_safe
from django.views import View

from base.forms import *
from inscricao.forms import *
from inscricao.models import *
#from inscricao.admin import AgenciaInline
from util.email import sendmail
from util.models import UserToken, create_token, valid_token


class HomeView(View):
    def get(self, request, **kwargs):
        return redirect('/login/')


class LoginView(View):
    template = 'base/login.html'
    dados = {}

    def get(self, request, **kwargs):
        if request.user.is_authenticated:
            return redirect('/admin')

        self.dados['formulario_login'] = LoginForm()
        if 'next' in request.GET:
            request.session['next'] = request.GET.get('next')
        return render(request, self.template, self.dados)

    def post(self, request, **kwargs):
        self.dados['formulario_login'] = LoginForm(request.POST)
        if self.dados['formulario_login'].is_valid():

            login_str = self.dados['formulario_login'].cleaned_data['usuario']
            if '@' in login_str:
                user = User.objects.filter(email=login_str)
                if user:
                    login_str = user.get()

            usuario = authenticate(
                    username=login_str,
                    password=self.dados['formulario_login'].cleaned_data['senha']
            )

            if usuario:
                if usuario.is_active:
                    login(request, usuario)

                    if 'next' in request.session:
                        retorno = request.session['next']
                        del request.session['next']
                        return redirect(retorno)
                    else:
                        return redirect('/admin')
                else:
                    messages.warning(request, 'Conta desabilitada. Entre em contato com a sua regional.')
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

            email = self.dados['formulario_registro'].cleaned_data['email']
            try:
                user = User.objects.get(email=email, is_active=False)
            except User.DoesNotExist:
                user = User.objects.create(
                    username=create_token(10),
                    first_name=self.dados['formulario_registro'].cleaned_data['nome'],
                    last_name=self.dados['formulario_registro'].cleaned_data['sobrenome'],
                    email=email,
                    is_active=False
                )

            token = UserToken.objects.create(owner=user.username)

            sendmail(
                to=[ self.dados['formulario_registro'].cleaned_data['email'], ],
                subject=u'Registro do Prêmio Colunistas',
                params={'site_name': 'Colunistas', 'nome': user.first_name, 'link': token.link()},
                template='emails/confirma-email.html', )

            return redirect('instrucoes-login')
        return render(request, self.template, self.dados)


class Registro2View(View):
    template = 'base/registro2.html'
    dados = {}

    def get(self, request, **kwargs):
        if UserToken.objects.filter(token = self.kwargs['token']).exists():
            self.dados['formulario_registro'] = Registro2Form()
            self.dados['formulario_registro'].fields['usuario'].required = True
            self.dados['token_usuario'] = self.kwargs['token']
        else:
            self.dados['token_usuario'] = 'invalid'
            messages.error(request, mark_safe('Pré-cadastro não encontrado ou expirado. Clique <a href="/registro/">aqui</a> para solicitar o seu pré-cadastro.'))
        return render(request, self.template, self.dados)

    def post(self, request, **kwargs):
        self.dados['formulario_registro'] = Registro2Form(request.POST)

        if not request.POST.get('usuario'):
            self.dados['formulario_registro'].add_error('usuario', 'O campo usuário é obrigatório.')
        elif User.objects.filter(username=request.POST.get('usuario')).exists():
            self.dados['formulario_registro'].add_error('usuario',
                    'Esse nome de usuário já foi utilizado. Por favor, escolha outro.')

        if self.dados['formulario_registro'].is_valid():
            try:
                user = User.objects.get(
                    username=UserToken.objects.get(token=self.kwargs['token']).owner,
                )
                if valid_token(owner=user.username, tk=UserToken.objects.get(owner=user.username).token):
                    user.username = self.dados['formulario_registro'].cleaned_data['usuario']
                    user.set_password(self.dados['formulario_registro'].cleaned_data['senha'])
                    user.is_active = True
                    user.is_staff = True
                    user.groups.add(Group.objects.get_or_create(name='Agência')[0])
                    user.save()

                    # Criando inscricao.Usuario
                    user_inscr = Usuario(nome_completo=user.get_full_name(), user=user)
                    user_inscr.save()

                    login(request, user)

                    messages.success(request, 'Usuário cadastrado com sucesso.')
                    return redirect('/admin/inscricao/empresa/add')
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


class InstrucoesResetLoginView(View):
    template = 'base/instrucoes-reset-login.html'
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
                if User.objects.filter(email=self.dados['formulario'].cleaned_data['email']).exists():
                    user = User.objects.get(email=self.dados['formulario'].cleaned_data['email'])
                    token = UserToken.objects.create(owner=user.username)
                    
                    sendmail(
                        to=[ self.dados['formulario'].cleaned_data['email'], ],
                        subject=u'Recuperação de senha do Prêmio Colunistas',
                        params={'site_name': 'Colunistas', 'nome': user.first_name, 'link': token.link_reset()},
                        template='emails/reseta-password.html', )
                else:
                    messages.warning(request, 'Usuário não cadastrado.')
                    return render(request, self.template, self.dados)
            except Exception as erro:
                messages.error(request, 'Erro: {}'.format(erro.__str__()))
        return redirect('instrucoes-reset-login')


class ReiniciaSenha2View(View):
    template = 'base/reinicia-senha2.html'
    dados = {}

    def get(self, request, **kwargs):
        if UserToken.objects.filter(token=self.kwargs['token']).exists():
            self.dados['formulario'] = Registro2Form()
            self.dados['formulario'].fields['usuario'].initial = UserToken.objects.get(token = self.kwargs['token']).owner
            self.dados['formulario'].fields['usuario'].widget.attrs['readonly'] = True
            self.dados['token'] = self.kwargs['token']
            return render(request, self.template, self.dados)
        else:
            self.dados['formulario'] =  'readonly'
            messages.error(request, 'Usuário não encontrado ou link expirado.\n Por favor clique em recuperar senha novamente')
            return redirect('reset-senha')

    def post(self, request, **kwargs):
        if UserToken.objects.filter(token = self.kwargs['token']).exists():
            self.dados['formulario'] = Registro2Form(request.POST)

            if self.dados['formulario'].is_valid():
                try:
                    user = User.objects.get(username = UserToken.objects.get(token = self.kwargs['token']).owner)
                    if valid_token(owner = user.username, tk = self.kwargs['token']):
                        user.set_password(self.dados['formulario'].cleaned_data['senha'])
                        user.save()
                        login(request, user)
                        return redirect('/admin')
                    else:
                        messages.error(request, 'Token inválido.')
                except Exception as erro:
                    messages.error(request, 'Erro: {}'.format(erro.__str__()))

        return render(request, self.template, self.dados)


def logoutview(request):
    logout(request)
    return redirect('login')

