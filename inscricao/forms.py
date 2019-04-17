#coding: utf-8
from django import forms
from inscricao.models import *
from util.fields import BRPhoneNumberField
from localflavor.br.forms import BRCNPJField
from base.forms import CAMPO_TEXTO_PADRAO, CAMPO_EMAIL_PADRAO, CAMPO_SENHA_PADRAO


class RegistroEmpresaForm(forms.ModelForm):
    telefone = BRPhoneNumberField(required = False)
    celular = BRPhoneNumberField(required = False)
    VP_Telefone = BRPhoneNumberField(required = False)
    C1_Telefone = BRPhoneNumberField(required = False)
    C2_Telefone = BRPhoneNumberField(required = False)

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

class RegistroEmpresaAgenciaForm(forms.ModelForm):
    class Meta:
        model = EmpresaAgencia
        fields = [
            'agencia', 'uf'
        ]

class RegistroRegionalForm(forms.ModelForm):
    class Meta:
        model = Regional
        fields = [
            'nome', 'estados',
        ]

class DadosFiscaisEmpresaForm(forms.Form):
    cnpj = BRCNPJField(label = 'CNPJ', widget = CAMPO_TEXTO_PADRAO)
    inscricao_estadual = forms.CharField(label = 'Inscrição Estadual', required = False, widget = CAMPO_TEXTO_PADRAO)
    inscricao_municipal = forms.CharField(label = 'Inscrição Municipal', required = False, widget = CAMPO_TEXTO_PADRAO)
