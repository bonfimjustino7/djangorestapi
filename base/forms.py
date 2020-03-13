#coding: utf-8
from django import forms
from django.forms import ModelForm
from django.core.exceptions import ValidationError

from .models import *


CAMPO_TEXTO_PADRAO = forms.widgets.TextInput(attrs={'class': 'input'})
CAMPO_EMAIL_PADRAO = forms.widgets.EmailInput(attrs={'class': 'input'})
CAMPO_SENHA_PADRAO = forms.widgets.PasswordInput(attrs={'class': 'input'})


class LoginForm(forms.Form):
    usuario = forms.CharField(
        required=True,
        label='Usuário',
        widget=forms.widgets.TextInput(attrs={'class': 'input', 'placeholder': 'Usuário'}),
    )
    senha = forms.CharField(
        required=True,
        widget=forms.widgets.PasswordInput(attrs={'class': 'input', 'placeholder': 'Senha'}),
    )


class Registro1Form(forms.Form):
    nome = forms.CharField(
        required=True,
        widget=forms.widgets.TextInput(attrs={'class': 'input', 'placeholder': 'Nome'}),
    )
    sobrenome = forms.CharField(
        required=True,
        widget=forms.widgets.TextInput(attrs={'class': 'input', 'placeholder': 'Sobrenome'}),
    )
    email = forms.EmailField(
        required=True,
        label='E-mail',
        widget=forms.widgets.EmailInput(attrs={'class': 'input', 'placeholder': 'E-mail'}),
    )

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email,is_active=True).exists():
            raise ValidationError('Já existe um usuário utilizando este e-mail')
        return email


class Registro2Form(forms.Form):
    usuario = forms.CharField(
        label='Digite um login',
        widget=forms.widgets.TextInput(attrs = {'class': 'input', 'placeholder': 'Nome de Usuário'})
    )
    senha = forms.CharField(
        required = True,
        widget = forms.widgets.PasswordInput(attrs = {'class': 'input', 'placeholder': 'Nova Senha'})
    )
    senha2 = forms.CharField(
        required=True,
        label='Repita a senha',
        widget=forms.widgets.PasswordInput(attrs = {'class': 'input', 'placeholder': 'Repita a Senha'})
    )

    def clean(self):
        dados = super().clean()

        if dados['senha'] != dados['senha2']:
            self.add_error('senha', 'As senhas não coincidem')
            self.add_error('senha2', 'As senhas não coincidem')


class ResetSenhaForm(forms.Form):
    email = forms.EmailField(
        required=True,
        label='E-mail',
        widget=forms.widgets.EmailInput(attrs = {'class': 'input', 'placeholder': 'E-mail'})
    )


class PrecoForm(ModelForm):
    categoria = ChainedForeignKey(Categoria, chained_field='premiacao', chained_model_field='premiacao',
                                  blank=True, null=True, help_text='Deixe em branco para o caso geral',
                                  show_all=False, on_delete=models.PROTECT)

    class Meta:
        model = Preco
        exclude = ('premiacao',)

    def __init__(self, *args, **kwargs):
        super(PrecoForm, self).__init__(*args, **kwargs)
        self.fields['categoria'].empty_label = "Qualquer categoria"
