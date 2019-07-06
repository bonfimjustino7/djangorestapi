from collections import OrderedDict
from genericpath import exists
from ntpath import exists
from os.path import exists

from django.contrib import messages
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
from inscricao.admin import AgenciaInline
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
                messages.warning(request, 'Entre com o seu login e não com o email')
                return render(request, self.template, self.dados)

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
                    return redirect('nova-empresa')
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
                    
                    sendmail(
                        to=[ self.dados['formulario'].cleaned_data['email'], ],
                        subject=u'Recuperação de senha do Prêmio Colunistas',
                        params={'site_name': 'Colunistas', 'nome': user.first_name, 'link': token.link()},
                        template='base/reinicia-senha.html', )

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
        if UserToken.objects.filter(token=self.kwargs['token']).exists():
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
    template = 'base/nova-empresa-2.html'
    dados = {}

    def get(self, request, **kwargs):
        id = request.GET.get('id', None)
        if id:
            empresa = Empresa.objects.get(id=id)
            request.session['empresa'] = empresa.id
            empresa_agencia = EmpresaAgencia.objects.filter(empresa__id=id)
            self.dados['id_empresa'] = empresa.id
            self.dados['formulario_cadastro'] = RegistroEmpresaForm(instance=empresa)
            self.dados['formulario_fiscal'] = DadosFiscaisEmpresaForm()
            self.dados['formset_agencias'] = RegistroEmpresaAgenciaForm(instance=empresa)
        else:  
            self.dados['formulario_cadastro'] = RegistroEmpresaForm()
            self.dados['formulario_fiscal'] = DadosFiscaisEmpresaForm()
            self.dados['formset_agencias'] = formset_factory(RegistroEmpresaAgenciaForm, extra=0)
            self.dados['id_empresa'] = 0
        return render(request, self.template, self.dados)

    def post(self, request, **kwargs):
        resposta = {}
        agencia_exists = False
        if request.POST.get('id') is None:
            formulario = RegistroEmpresaForm(request.POST)
            emp = None
        else:
            emp = Empresa.objects.get(pk=int(request.POST.get('id')))
            formulario = RegistroEmpresaForm(request.POST, instance=emp)
        formset_agencias = formset_factory(RegistroEmpresaAgenciaForm)(request.POST)

        nome_empresa = request.POST.get('nome').strip().upper()
        email = request.POST.get('email')
        vp_email = request.POST.get('VP_Email')
        c1_email = request.POST.get('C1_Email')
        c2_email = request.POST.get('C2_Email')
    

        if email == vp_email and email != '' and vp_email != '':
            formulario.add_error('email', 'E-mail do VP deve ser diferentes')

        if email == c1_email and email != '' and c1_email != '':
            formulario.add_error('email', 'E-mail do Contato 1 devem ser diferentes')

        if email == c2_email and email != '' and c2_email != '':
            formulario.add_error('email', 'E-mail do Contato 2 devem ser diferentes')

        if vp_email == c1_email and vp_email != '' and c1_email != '':
            formulario.add_error('VP_Email', 'E-mails do VP e do Contato 1 devem ser diferentes')

        if vp_email == c2_email and vp_email != '' and c2_email != '':
            formulario.add_error('VP_Email', 'E-mails do VP e do Contato 2 devem ser diferentes')

        if c1_email == c2_email and c1_email != '' and c2_email != '':
            formulario.add_error('C1_Email', 'E-mails do contato 1 e 2 devem ser diferentes')

        if emp:
            emp_id = emp.id
        else:
            emp_id = 0

        if Empresa.objects.filter(nome=nome_empresa).exclude(pk=emp_id).exists():
            formulario.add_error('nome', 'Já existe uma empresa cadastrada com esse nome. Por favor, utilize outro.')

        if formulario.is_valid():
            try:
                # Salvando Empresa

                empresa = formulario.save()
                resposta['pk'] = empresa.pk

                # Salvando EmpresaUsuario
                usuario = Usuario.objects.get(user=request.user)
                EmpresaUsuario.objects.get_or_create(empresa=empresa, usuario=usuario)

                # Salvando primeira agencia
                area = request.POST.get('area')
                agencia=EmpresaAgencia.objects.filter(empresa_id=empresa.pk)
                if not agencia.exists():
                    if (area == '1') or (area == '3') or (area == '27'):
                        empresa.empresaagencia_set.create(
                            agencia=request.POST.get('nome'),
                            uf=UF.objects.get(sigla=request.POST.get('uf')) 
                        )    
                        agencia_exists = True    
                # Salvando objetos EmpresaAgencia
               
                for i in range(0, int(request.POST.get('form-TOTAL_FORMS'))):
                    print(request.POST.get('form-{}-nome'.format(i)), request.POST.get('form-{}-uf'.format(i)))
                    if request.POST.get('form-{}-nome'.format(i)) == '' or request.POST.get('form-{}-uf'.format(i)) == '':
                        pass
                    else:
                        agencia_full=EmpresaAgencia.objects.filter(empresa_id=empresa.pk, agencia=request.POST.get('form-{}-nome'.format(i)))
                        if not agencia_full.exists() : 
                            uf= UF.objects.get(sigla=request.POST.get('form-{}-uf'.format(i)))
                            empresa.empresaagencia_set.create(
                            agencia=request.POST.get('form-{}-nome'.format(i)),
                            uf=uf
                            )
                            agencia_exists = True
                             
                resposta['agencia_full'] = agencia_exists          
                request.session['empresa'] = empresa.id
                resposta['status'] = 200

            except Exception as erro:
                if empresa:
                    request.session['empresa'] = empresa.id
                resposta['status'] = 500
                resposta['texto'] = erro.__str__()
        else:
            print(formulario.cleaned_data)
            print(formulario.errors)
            resposta['status'] = 500
            erros = formulario.errors.items()
            texto = formulario.errors.as_text()
            for e in erros:
                label = Empresa._meta.get_field(e[0]).verbose_name
                if label is not None:
                    texto = texto.replace(e[0], label)
                else:
                    pass
                print(e[0], e[1], Empresa._meta.get_field(e[0]).verbose_name)

            resposta['texto'] = texto
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


def consulta_agencia(request, empresa):
    resposta = {}
    if EmpresaAgencia.objects.filter(empresa_id = empresa.pk).exists():
        resposta['agencia'] = True
    else:
        resposta['agencia'] = False
    return JsonResponse(resposta)


def estados_regional(request):
    id_regional = request.GET.get('regional')
    if int(id_regional) > 0:
        resposta = {
            'estados': Regional.objects.get(id = id_regional).estados.split(','),
        }
    else:
        lista = []
        regionais = Regional.objects.all()
        for r in regionais:
            estados = r.estados.split(',')
            for e in estados:
                lista.append(e)
        resposta = {
                'estados': lista,
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
