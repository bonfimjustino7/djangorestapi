#coding: utf-8
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import *
from .forms import *
from .models import *
from django.views import View

def gerar_token(tamanho = 32):
	chars = []
	chars.extend([i for i in string.ascii_letters])
	chars.extend([i for i in string.digits])
	#chars.extend([i for i in '#$%*'])

	passwd = ''

	for i in range(tamanho):
		passwd += chars[random.randint(0,  len(chars) - 1)]

		random.seed = int(time.time())
		random.shuffle(chars)

return passwd

class LoginView(View):
	template = ''
	dados = {}

	def get(self, request, **kwargs):
		self.dados = inicializa_dados()
		self.dados['formulario_login'] = LoginForm()
		if 'next' in request.GET:
			request.session['next'] = request.GET.get('next')
		return render(request, self.template, self.dados)

	def post(self, request, **kwargs):
		self.dados = inicializa_dados()
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
				usuario = Usuario.objects.create(
					token = gerar_token()
				)

				mensagem = 'Olá {},\nVocê demonstrou interesse em realizar o cadastro no site Colunistas.\nPara completar o seu cadastro, clique no link ou copie o endereço no seu navegador:\n{}/novo-usuario/{}/{}/{}/{}/\nAtenciosamente,\nEquipe Colunistas'.format(
					self.dados['formulario_registro'].cleaned_data['nome'],
					settings.SITE_HOST,
					usuario.token,
					self.dados['formulario_registro'].cleaned_data['nome'],
					self.dados['formulario_registro'].cleaned_data['sobrenome'],
					self.dados['formulario_registro'].cleaned_data['email'],
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
				'nome': self.kwargs['nome'],
				'sobrenome': self.kwargs['sobrenome'],
				'email': self.kwargs['email'],
			}
		else:
			messages.error(request, 'Pré-cadastro não encontrado.')
		return render(request, self.template, self.dados)

	def post(self, request, **kwargs):
		self.dados['formulario_registro'] = Registro2Form(request.POST)
		if self.dados['formulario_registro'].is_valid():
			try:
				usuario = Usuario.objects.get(token = request.session['usuario']['token'])
				usuario.user = User.objects.create(
					first_name = request.session['usuario']['nome'],
					last_name = request.session['usuario']['sobrenome'],
					email = request.session['usuario']['email'],
					username = self.dados['formulario_registro'].cleaned_data['usuario'],
				)
				usuario.user.set_password(self.dados['formulario_registro'].cleaned_data['senha'])
				usuario.save()

				del request.session['usuario']

				messages.success(request, 'Usuário cadastrado com sucesso.')
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
				usuario = Usuario.objects.get(user__email = self.dados['formulario'].cleaned_data['email'])

				#Modifica o token do usuario:
				usuario.token = gerar_token()
				usuario.save()

				mensagem = 'Olá {},\nFoi solicitado ao sistema modificar a sua senha no nosso site.\nPara realizar essa operação, clique no link abaixo ou copie o endereço em seu navegador:\n\n{}/nova-senha/{}/\n\nCaso você não tenha solicitado uma nova senha, desconsidere essa mensagem.\nAtenciosamente,\nEquipe Colunistas'.format(
					usuario.user.first_name,
					settings.SITE_HOST,
					usuario.token,
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
		if Usuario.objects.filter(token = self.kwargs['token']).exists():
			self.dados['formulario'] = Registro2Form()
			self.dados['formulario'].fields['usuario'].required = False
			self.dados['formulario'].fields['usuario'].disabled = True

			request.session['usuario'] = Usuario.objects.get(token = self.kwargs['token']).id
		else:
			messages.error(request, 'Usuário não encontrado.')

		return render(request, self.template, self.dados)

	def post(self, request, **kwargs):
		usuario = Usuario.objects.get(id = request.session['usuario'])
		self.dados['formulario'] = Registro2Form(request.POST)
		if self.dados['formulario'].is_valid():
			try:
				usuario.user.set_password(self.dados['formulario'].cleaned_data['senha'])
				messages.success(request, 'Senha alterada com sucesso.')
			except:
				messages.error(request, 'Erro ao alterar a senha.')
		return render(request, self.template, self.dados)

class InicioView(LoginRequiredMixin, View):
	template = ''
	dados = {}

	def get(self, request, **kwargs):
		return render(request, self.template, self.dados)

def logoutview(request):
	logout(request)
