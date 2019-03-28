#coding: utf-8
from django import forms

CAMPO_TEXTO_PADRAO = forms.widgets.TextInput(attrs = {})
CAMPO_EMAIL_PADRAO = forms.widgets.EmailInput(attrs = {})
CAMPO_SENHA_PADRAO = forms.widgets.PasswordInput(attrs = {})

class LoginForm(forms.Form):
	usuario = forms.CharField(required = True, label = 'Usuário', widget = CAMPO_TEXTO_PADRAO)
	senha = forms.CharField(required = True, widget = CAMPO_SENHA_PADRAO)

class Registro1Form(forms.Form): # TODO: Incluir o captcha do Google
	nome = forms.CharField(required = True, widget = CAMPO_TEXTO_PADRAO)
	sobrenome = forms.CharField(required = True, widget = CAMPO_TEXTO_PADRAO)
	email = forms.EmailField(required = True, label = 'E-mail', widget = CAMPO_EMAIL_PADRAO)

class Registro2Form(forms.Form):
	usuario = forms.CharField(required = True, label = 'Usuário', widget = CAMPO_TEXTO_PADRAO)
	senha = forms.CharField(required = True, widget = CAMPO_SENHA_PADRAO)
	senha2 = forms.CharField(required = True, label = 'Repita a senha', widget = CAMPO_SENHA_PADRAO)

	def clean(self):
		dados = super().clean()

		if dados['senha'] != dados['senha2']:
			self.add_error('senha', 'As senhas não coincidem')
			self.add_error('senha2', 'As senhas não coincidem')

class ResetSenhaForm(forms.Form):
	email = forms.EmailField(required = True, label = 'E-mail', widget = CAMPO_EMAIL_PADRAO)
