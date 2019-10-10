#coding: utf-8
from django import forms
from inscricao.models import *
from util.fields import BRPhoneNumberField, BRZipCodeField
from localflavor.br.forms import BRCNPJField
from base.forms import CAMPO_TEXTO_PADRAO


class RegistroEmpresaForm(forms.ModelForm):
    cep = forms.CharField(max_length=9, required=True, widget=forms.TextInput(attrs={'data-mask':"00000-000"}))
    telefone = forms.CharField(max_length=9, required=True, widget=forms.TextInput(attrs={'data-mask':"0000-0000"}))
    celular = BRPhoneNumberField(required=False)
    VP_Telefone = forms.CharField(max_length=9, required=True, widget=forms.TextInput(attrs={'data-mask':"0000-0000"}))
    C1_Telefone = forms.CharField(max_length=9, required=True, widget=forms.TextInput(attrs={'data-mask':"0000-0000"}))
    C2_Telefone = forms.CharField(max_length=9, required=True, widget=forms.TextInput(attrs={'data-mask':"0000-0000"}))
    endereco = forms.CharField(max_length=100, required=True)
    bairro = forms.CharField(max_length=20, required=True)
    telefone = forms.CharField(max_length=9, required=True, widget=forms.TextInput(attrs={'data-mask':"0000-0000"}))
    celular = forms.CharField(max_length=9, required=True, widget=forms.TextInput(attrs={'data-mask':"0000-0000"}))
    email = forms.EmailField(required=True, help_text='Apenas se a empresa tiver um email central')
    homepage = forms.URLField(required=True)
    VP_Telefone = forms.CharField(max_length=9, help_text=u'XXXXX-XXXX', required=True, widget=forms.TextInput(attrs={'data-mask':"0000-0000"}))
    VP_Email = forms.EmailField(required=True)

    VP_Telefone = forms.CharField(label='', max_length=9, required=True, help_text=u'XXXXX-XXXX', widget=forms.TextInput(attrs={'data-mask':"0000-0000"}))
    C1_Nome = forms.CharField(label='VP ou Diretor da Empresa', required=True)
    C1_Cargo = forms.CharField(label='Cargo VP ou Diretor', max_length=60, required=True)
    C1_Email = forms.EmailField(label='Email', required=True)
    C1_DDD = forms.CharField(label='DDD', max_length=2,required=True)
    C1_Telefone = forms.CharField(label='Telefone', max_length=9, required=True, help_text=u'XXXXX-XXXX', widget=forms.TextInput(attrs={'data-mask':"0000-0000"}))
    C2_Nome = forms.CharField(label='VP ou Diretor da Empresa', max_length=100, required=True)
    C2_Cargo = forms.CharField(label='Cargo VP ou Diretor', max_length=60, required=True)
    C2_Email = forms.EmailField(label='Email', required=True)
    C2_DDD = forms.CharField(label='DDD', max_length=2, required=True, )
    C2_Telefone = forms.CharField(label='Telefone', max_length=9, required=True, help_text=u'XXXXX-XXXX', widget=forms.TextInput(attrs={'data-mask':"0000-0000"}))

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

    def clean(self):

        nome_empresa = self.cleaned_data.get('nome').strip().upper()
        email = self.cleaned_data.get('email')
        vp_email = self.cleaned_data.get('VP_Email')
        c1_email = self.cleaned_data.get('C1_Email')
        c2_email = self.cleaned_data.get('C2_Email')

        if email == vp_email and email != '' and vp_email != '':
            self._errors['email'] = self.error_class(['E-mail do VP deve ser diferentes'])

        if email == c1_email and email != '' and c1_email != '':
            self._errors['email'] = self.error_class(['E-mail do Contato 1 devem ser diferentes'])

        if email == c2_email and email != '' and c2_email != '':
            self._errors['email'] = self.error_class(['E-mail do Contato 2 devem ser diferentes'])

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
    cnpj = BRCNPJField(label = 'CNPJ', widget = CAMPO_TEXTO_PADRAO)
    inscricao_estadual = forms.CharField(label = 'Inscrição Estadual', required = False, widget = CAMPO_TEXTO_PADRAO)
    inscricao_municipal = forms.CharField(label = 'Inscrição Municipal', required = False, widget = CAMPO_TEXTO_PADRAO)
