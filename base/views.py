from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.http import JsonResponse
from django.contrib.auth.models import User, Group

from django.contrib import messages

from django.forms import formset_factory

from util.models import create_token, UserToken, valid_token
from util.email import sendmail

from base.forms import *
from inscricao.forms import *
from inscricao.models import *


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

            user = User.objects.create(
                username=create_token(10),
                first_name=self.dados['formulario_registro'].cleaned_data['nome'],
                last_name=self.dados['formulario_registro'].cleaned_data['sobrenome'],
                email=self.dados['formulario_registro'].cleaned_data['email'],
                is_active=False
            )

            token = UserToken.objects.create(owner=user.username)

            sendmail(
                to=[ self.dados['formulario_registro'].cleaned_data['email'], ],
                subject=u'Registro do Prêmio Colunistas',
                params={'site_name': 'Colunistas', 'nome': user.first_name, 'link': token.link()},
                template='emails/confirma-email.html', )

            messages.success(request, 'Verifique seu e-mail para completar o registro')
        return redirect('instrucoes-login')


class Registro2View(View):
    template = 'base/registro2.html'
    dados = {}

    def get(self, request, **kwargs):
        self.dados['formulario_registro'] = Registro2Form()
        if UserToken.objects.filter(token = self.kwargs['token']).exists():
            self.dados['token_usuario'] = self.kwargs['token']
        else:
            messages.error(request, 'Pré-cadastro não encontrado')
        return render(request, self.template, self.dados)

    def post(self, request, **kwargs):
        self.dados['formulario_registro'] = Registro2Form(request.POST)

        if not request.POST.get('usuario'):
            self.dados['formulario_registro'].add_error('usuario', 'O campo usuário é obrigatório.')
        elif User.objects.filter(username = request.POST.get('usuario')).exists():
            self.dados['formulario_registro'].add_error('usuario',
                    'Esse nome de usuário já foi utilizado. Por favor, escolha outro.')

        if self.dados['formulario_registro'].is_valid():
            try:
                user = User.objects.get(
                    username=UserToken.objects.get(token = self.kwargs['token']).owner,
                )
                if valid_token(owner = user.username, tk = UserToken.objects.get(owner = user.username).token):
                    user.username = self.dados['formulario_registro'].cleaned_data['usuario']
                    user.set_password(self.dados['formulario_registro'].cleaned_data['senha'])
                    user.is_active = True
                    user.is_staff = True
                    grupo = Group.objects.get_or_create(name='Agência')
                    user.groups.add(grupo)
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
                    token = UserToken.objects.create(owner = user.username)

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
        self.dados['formset_agencias'] = formset_factory(RegistroEmpresaAgenciaForm, extra = 0)
        return render(request, self.template, self.dados)

    def post(self, request, **kwargs):
        resposta = {}
        formulario = RegistroEmpresaForm(request.POST)
        formset_agencias = formset_factory(RegistroEmpresaAgenciaForm)(request.POST)

        if Empresa.objects.filter(nome = request.POST.get('nome')).exists():
            formulario.add_error('nome', 'Já existe uma empresa cadastrada com esse nome. Por favor, utilize outro.')

        if formulario.is_valid():
            try:
                # Salvando Empresa
                empresa = formulario.save()

                # Salvando EmpresaUsuario
                empresa.empresausuario_set.create(
                    usuario = request.user.usuario_set.first(),
                )

                # Salvando objetos EmpresaAgencia
                for i in range(0, int(request.POST.get('form-TOTAL_FORMS'))):
                    print(request.POST.get('form-{}-nome'.format(i)), request.POST.get('form-{}-uf'.format(i)))
                    empresa.empresaagencia_set.create(
                        agencia = request.POST.get('form-{}-nome'.format(i)),
                        uf = UF.objects.get(sigla = request.POST.get('form-{}-uf'.format(i))),
                    )

                request.session['empresa'] = empresa.id

                resposta['status'] = 200
            except Exception as erro:
                resposta['status'] = 500
                resposta['texto'] = 'Erro: {}'.format(erro.__str__())
        else:
            print(formulario.cleaned_data)
            print(formulario.errors)
            resposta['status'] = 500
            resposta['texto'] = formulario.errors.as_text()
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

def estados_regional(request):
    resposta = {
        'estados': Regional.objects.get(id = request.GET.get('regional')).estados.split(','),
    }
    return JsonResponse(resposta)

def cadastro_fiscal(request):
    # TODO: Desenvolver cadastros fiscais
    resposta = {}
    if request.POST:
        formulario = DadosFiscaisEmpresaForm(request.POST)
        if formulario.is_valid():
            try:
                empresa = Empresa.objects.get(id = request.session['empresa'])
                resposta['status'] = 200
            except Exception as erro:
                resposta['status'] = 500
                resposta['texto'] = erro.__str__()
        else:
            resposta['status'] = 500
            resposta['texto'] = 'Dados incorretos. Por favor, tente novamente.'
    else:
        resposta['status'] = 500
        resposta['texto'] = 'Método de requisição inválido.'
    return JsonResponse(resposta)
