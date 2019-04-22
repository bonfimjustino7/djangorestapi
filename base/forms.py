#coding: utf-8
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

CAMPO_TEXTO_PADRAO = forms.widgets.TextInput(attrs = {'class': 'input'})
CAMPO_EMAIL_PADRAO = forms.widgets.EmailInput(attrs = {'class': 'input'})
CAMPO_SENHA_PADRAO = forms.widgets.PasswordInput(attrs = {'class': 'input'})


class LoginForm(forms.Form):
    usuario = forms.CharField(required=True, label='Usuário', widget=CAMPO_TEXTO_PADRAO,
                              help_text='Entre com o nome do usuário (obrigatório)')
    senha = forms.CharField(required=True, widget=CAMPO_SENHA_PADRAO, help_text='Digite a senha')


class Registro1Form(forms.Form):  # TODO: Incluir o captcha do Google
    nome = forms.CharField(required=True, widget=CAMPO_TEXTO_PADRAO,
                           help_text='Digite o seu primeiro nome (obrigatório)')
    sobrenome = forms.CharField(required=True, widget = CAMPO_TEXTO_PADRAO,
                                help_text='Digite o seu sobrenome (obrigatório)')
    email = forms.EmailField(required=True, label = 'E-mail', widget=CAMPO_EMAIL_PADRAO,
                             help_text='Digite o seu email (obrigatório)')

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email = email, is_active = True).exists():
            raise ValidationError('Já existe um usuário utilizando este email')
        return email


class Registro2Form(forms.Form):
    usuario = forms.CharField(label='Digite um login', widget=CAMPO_TEXTO_PADRAO)
    senha = forms.CharField(required=True, widget=CAMPO_SENHA_PADRAO)
    senha2 = forms.CharField(required=True, label='Repita a senha', widget=CAMPO_SENHA_PADRAO)

    def clean(self):
        dados = super().clean()

        if dados['senha'] != dados['senha2']:
            self.add_error('senha', 'As senhas não coincidem')
            self.add_error('senha2', 'As senhas não coincidem')


class ResetSenhaForm(forms.Form):
    email = forms.EmailField(required = True, label = 'E-mail', widget = CAMPO_EMAIL_PADRAO)
