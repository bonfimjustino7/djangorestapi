#coding: utf-8
from django import forms
from django.forms import ModelForm, ModelChoiceField

from inscricao.models import *
from util.fields import BRPhoneNumberField, BRZipCodeField
from localflavor.br.forms import BRCNPJField
from base.forms import CAMPO_TEXTO_PADRAO
from .models import *


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

class RegistroEmpresaForm(forms.ModelForm):
    regional = forms.ModelChoiceField(queryset=Regional.objects.all(), help_text='Consulte o regulamento para saber em qual delas a sua região se enquadra.', required=True)
    nome = forms.CharField(label='Nome da Empresa', max_length=30, help_text='Use o nome de fantasia simplificado da empresa, sem "Ltda", "Propaganda", "Comunicação", "Criação", "Promoções", etc.')
    area = forms.ModelChoiceField(label='Área de Atuação', queryset=Area.objects.all(), help_text='Escolha a que mais se aproxime da sua principal área de atuação.')
    cep = forms.CharField(max_length=9, required=True, widget=forms.TextInput(attrs={'data-mask':"00000-000"}), help_text='Digite no formato 00000-000')
    C1_Telefone = forms.CharField(max_length=9, required=True, widget=forms.TextInput(attrs={'data-mask':"00000-0000"}))
    C2_Telefone = forms.CharField(max_length=9, required=True, widget=forms.TextInput(attrs={'data-mask':"00000-0000"}))
    endereco = forms.CharField(max_length=100, required=True)
    bairro = forms.CharField(max_length=20, required=True)
    telefone = forms.CharField(label='Telefone 1', max_length=9, required=False)
    celular = forms.CharField(label='Telefone 2',max_length=9, required=False)
    email = forms.EmailField(required=False, help_text='Apenas se a empresa tiver um email central')
    homepage = forms.URLField(required=False, help_text=' Digite o endereço (URL) do site da empresa')
    VP_Email = forms.EmailField(required=True)

    VP_Telefone = forms.CharField(label='Telefone', max_length=9, required=True, widget=forms.TextInput(attrs={'data-mask':"00000-0000"}))
    C1_Nome = forms.CharField(label='VP ou Diretor da Empresa', required=False)
    C1_Cargo = forms.CharField(label='Cargo VP ou Diretor', max_length=60, required=False)
    C1_Email = forms.EmailField(label='Email', required=False)
    C1_DDD = forms.CharField(label='DDD', max_length=2,required=False)
    C1_Telefone = forms.CharField(label='Telefone', max_length=9, required=False, widget=forms.TextInput(attrs={'data-mask':"00000-0000"}))
    C2_Nome = forms.CharField(label='VP ou Diretor da Empresa', max_length=100, required=False)
    C2_Cargo = forms.CharField(label='Cargo VP ou Diretor', max_length=60, required=False)
    C2_Email = forms.EmailField(label='Email', required=False)
    C2_DDD = forms.CharField(label='DDD', max_length=2, required=False, )
    C2_Telefone = forms.CharField(label='Telefone', max_length=9, required=False, widget=forms.TextInput(attrs={'data-mask':"00000-0000"}))

    class Meta:
        model = Empresa
        fields = (
            'regional', 'nome', 'area',
            'cep', 'endereco', 'bairro', 'cidade', 'uf',
            'ddd', 'telefone', 'celular',
            'homepage', 'email',
            'VP_Nome', 'VP_Cargo', 'VP_Email', 'VP_DDD', 'VP_Telefone',
            'C1_Nome', 'C1_Cargo', 'C1_Email', 'C1_DDD', 'C1_Telefone',
            'C2_Nome', 'C2_Cargo', 'C2_Email', 'C2_DDD', 'C2_Telefone',
        )

    def clean_cep(self):
        email = self.cleaned_data['cep'].replace('-','')
        return email

    def clean_nome(self):
        nome = self.cleaned_data['nome'].upper()
        return nome

#    def clean_homepage(self):
#        texto = self.cleaned_data['homepage'].replace('http://', '').replace('https://', '')
#        return texto

    def clean(self):

        try:
            nome_empresa = self.cleaned_data.get('nome').strip().upper()
        except:
            nome_empresa = ''

        email = self.cleaned_data.get('email')
        vp_email = self.cleaned_data.get('VP_Email')
        vp_nome = self.cleaned_data.get('VP_Nome')

        c1_nome = self.cleaned_data.get('C1_Nome')
        c1_cargo = self.cleaned_data.get('C1_Cargo')
        c1_email = self.cleaned_data.get('C1_Email')
        c1_telefone = self.cleaned_data.get('C1_Telefone')

        c2_email = self.cleaned_data.get('C2_Email')
        c2_nome = self.cleaned_data.get('C2_Nome')
        c2_cargo = self.cleaned_data.get('C2_Cargo')
        c2_telefone = self.cleaned_data.get('C2_Telefone')

        if c1_nome:
            if not c1_cargo:
                self._errors['C1_Cargo'] = self.error_class(['Preencha este campo.'])
            if not c1_email:
                self._errors['C1_Email'] = self.error_class(['Preencha este campo.'])
            if not c1_telefone:
                self._errors['C1_Telefone'] = self.error_class(['Preencha este campo.'])
                self._errors['C1_DDD'] = self.error_class(['Preencha este campo.'])

        if c2_nome:
            if not c2_cargo:
                self._errors['C2_Cargo'] = self.error_class(['Preencha este campo.'])
            if not c2_email:
                self._errors['C2_Email'] = self.error_class(['Preencha este campo.'])
            if not c2_telefone:
                self._errors['C2_Telefone'] = self.error_class(['Preencha este campo.'])
                self._errors['C2_DDD'] = self.error_class(['Preencha este campo.'])

        if vp_nome == c1_nome and not vp_nome == '':
            self._errors['C1_Nome'] = self.error_class(['O nome do diretor VP deve ser diferente do Outros contatos da empresa'])

        if vp_nome == c2_nome and not vp_nome == '':
            self._errors['C2_Nome'] = self.error_class(
                ['O nome do diretor VP deve ser diferente de Outros contatos da empresa.'])
        if c1_nome == c2_nome and not c1_nome == '':
            self._errors['C1_Nome'] = self.error_class(
                ['Os nomes dos diretores não podem ser iguais.'])
            self._errors['C2_Nome'] = self.error_class(
                ['Os nomes dos diretores não podem ser iguais.'])

        if email == vp_email and email != '' and vp_email != '':
            self._errors['email'] = self.error_class(['E-mail do VP e da Empresa devem ser diferentes'])

        if email == c1_email and email != '' and c1_email != '':
            self._errors['email'] = self.error_class(['E-mail dos Contatos deve ser diferente'])

        if email == c2_email and email != '' and c2_email != '':
            self._errors['email'] = self.error_class(['E-mail dos Contatos deve ser diferente'])

        if vp_email == c1_email and vp_email != '' and c1_email != '':
            self._errors['VP_Email'] = self.error_class(['E-mails do VP e do Contato 1 devem ser diferentes'])

        if vp_email == c2_email and vp_email != '' and c2_email != '':
            self._errors['VP_Email'] = self.error_class(['E-mails do VP e do Contato 2 devem ser diferentes'])

        if c1_email == c2_email and c1_email != '' and c2_email != '':
            self._errors['C1_Email'] = self.error_class(['E-mails do contato 1 e 2 devem ser diferentes'])

        if Empresa.objects.filter(nome=nome_empresa).exclude(pk=self.instance.pk):
            self._errors['nome'] = self.error_class(['Já existe uma empresa cadastrada com esse nome. Por favor, utilize outro.'])

        return self.cleaned_data


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
    cnpj = BRCNPJField(label='CNPJ', widget=CAMPO_TEXTO_PADRAO)
    inscricao_estadual = forms.CharField(label='Inscrição Estadual', required=False, widget=CAMPO_TEXTO_PADRAO)
    inscricao_municipal = forms.CharField(label='Inscrição Municipal', required=False, widget=CAMPO_TEXTO_PADRAO)
