#coding: utf-8
from django import forms
from inscricao.models import Empresa

CAMPO_TEXTO_PADRAO = forms.widgets.TextInput(attrs = {'class': 'form-control'})
CAMPO_EMAIL_PADRAO = forms.widgets.EmailInput(attrs = {'class': 'form-control'})
CAMPO_SENHA_PADRAO = forms.widgets.PasswordInput(attrs = {'class': 'form-control'})


class LoginForm(forms.Form):
    usuario = forms.CharField(required=True, label = 'Usuário', widget = CAMPO_TEXTO_PADRAO)
    senha = forms.CharField(required=True, widget = CAMPO_SENHA_PADRAO)


class Registro1Form(forms.Form):  # TODO: Incluir o captcha do Google
    nome = forms.CharField(required=True, widget = CAMPO_TEXTO_PADRAO)
    sobrenome = forms.CharField(required=True, widget = CAMPO_TEXTO_PADRAO)
    email = forms.EmailField(required=True, label = 'E-mail', widget = CAMPO_EMAIL_PADRAO)


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


class RegistroEmpresaForm(forms.ModelForm):
    class Meta:
        model = Empresa
        fields = [
            'regional', 'nome', 'area',
            'cep', 'endereco', 'bairro', 'municipio', 'uf',
            'ddd', 'telefone', 'celular',
            'homepage', 'email',
            'VP_Nome', 'VP_Cargo', 'VP_Email', 'VP_DDD', 'VP_Telefone',
            'C1_Nome', 'C1_Cargo', 'C1_Email', 'C1_DDD', 'C1_Telefone',
            'C2_Nome', 'C2_Cargo', 'C2_Email', 'C2_DDD', 'C2_Telefone',
        ]
