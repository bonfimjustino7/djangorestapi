from django.contrib import admin
from django.shortcuts import get_object_or_404
from localflavor.md import forms
from tabbed_admin import TabbedModelAdmin

from base.models import *
from inscricao.models import *
from poweradmin.admin import (PowerButton, PowerModelAdmin, PowerStackedInline,
                              PowerTabularInline)
from django.contrib.messages import constants as messages

from base.views import *

change_form_template = 'admin/myapp/extras/openstreetmap_change_form.html'


class AgenciaInline(admin.TabularInline):
    model = EmpresaAgencia
    fields = ('agencia', 'uf', )
    extra = 0


@admin.register(EmpresaAgencia)
class EmpresaAgenciaAdmin(admin.ModelAdmin):
    list_display = ('agencia', 'empresa', 'uf')

    def get_queryset(self, request):
        qs = super(EmpresaAgenciaAdmin, self).get_queryset(request)
        if request.user.groups.filter(name='Agência'):
            usuario = Usuario.objects.filter(user=request.user)
            empresas = list(EmpresaUsuario.objects.filter(usuario = usuario).values_list('empresa_id', flat=True))
            qs = qs.filter(empresa__in=empresas)

        return qs

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'empresa':
            usuario = Usuario.objects.filter(user=request.user)
            empresas = list(EmpresaUsuario.objects.filter(usuario=usuario).values_list('empresa', flat=True))
            kwargs['queryset'] = Empresa.objects.filter(pk__in=empresas)
        return super(EmpresaAgenciaAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('user',)


@admin.register(EmpresaUsuario)
class EmpresaUsuarioAdmin(admin.ModelAdmin):
    list_display = ('empresa', 'usuario')


@admin.register(Empresa)
class EmpresaAdmin(PowerModelAdmin):
    list_filter = ('regional','area')
    list_display = ('nome', 'uf', 'cidade', 'area')

    def get_buttons(self, request, object_id):
        buttons = super(EmpresaAdmin, self).get_buttons(request, object_id)
        buttons.append(PowerButton(url='/admin/inscricao/inscricao/add', label=u'Adicionar Inscrição'))
        return buttons

    fieldsets = (
        ('EMPRESA RESPONSÁVEL PELA INSCRIÇÃO', {
           'fields': ('regional', ('nome', 'area'), ('cep', 'cidade', 'uf'), ('endereco', 'bairro'), ('ddd', 'telefone', 'celular'),('homepage', 'email'))
        }),
        ('VP OU DIRETOR RESPONSÁVEL PELAS INSCRIÇÕES', {
            'fields': (('VP_Nome', 'VP_Cargo'), ('VP_Email', 'VP_DDD', 'VP_Telefone'))
        }),
        ('OUTROS CONTATOS NA EMPRESA (Profissionais que também receberão as comunicações da Abracomp sobre a premiação.)', {
            'fields': (('C1_Nome', 'C1_Cargo', 'C1_Email', 'C1_DDD', 'C1_Telefone'), ('C2_Nome', 'C2_Cargo','C2_Email', 'C2_DDD', 'C2_Telefone',))
        }),
    )
    inlines = [AgenciaInline]
    form = RegistroEmpresaForm

    def get_form(self, request, obj=None, **kwargs):
        form = super(EmpresaAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['cep'].widget.attrs['style'] = 'width: 5em;'
        form.base_fields['ddd'].widget.attrs['style'] = 'width: 2em;'
        form.base_fields['VP_DDD'].widget.attrs['style'] = 'width: 2em;'
        form.base_fields['C1_DDD'].widget.attrs['style'] = 'width: 2em;'
        form.base_fields['C2_DDD'].widget.attrs['style'] = 'width: 2em;'
        form.base_fields['nome'].widget.attrs['style'] = 'width: 30em;'
        form.base_fields['endereco'].widget.attrs['style'] = 'width: 30em;'
        form.base_fields['bairro'].widget.attrs['style'] = 'width: 30em;'
        return form

    def get_queryset(self, request):
        qs = super(EmpresaAdmin, self).get_queryset(request)
        if request.user.groups.filter(name='Agência'):
            usuario = Usuario.objects.filter(user=request.user)
            empresas = list(EmpresaUsuario.objects.filter(usuario = usuario).values_list('empresa_id', flat=True))
            qs = qs.filter(pk__in=empresas)

        return qs

    def save_model(self, request, obj, form, change):
        area = form.cleaned_data['area'].pk
        obj.save()
        if not request.user.is_superuser:
            if area == 1 or area == 3 or area == 27:
                if not EmpresaAgencia.objects.filter(agencia=obj.nome).exists():
                    obj.empresaagencia_set.create(empresa=obj, agencia=obj.nome, uf=obj.uf)
            usuario = Usuario.objects.get(user=request.user)
            EmpresaUsuario.objects.get_or_create(usuario=usuario, empresa=obj)


class MaterialInline(admin.TabularInline):
    model = Material
    fields = ('tipo', 'arquivo', 'url', )
    extra = 1


@admin.register(Inscricao)
class InscricaoAdmin(PowerModelAdmin, TabbedModelAdmin):
    list_filter = ('premiacao', )
    # list_display = ('empresa', 'seq', 'titulo', 'categoria', 'cliente')
    readonly_fields = ('seq', )
    #actions = ('exportar', )
    tab_info = (
        (None, {'fields': (('premiacao', 'empresa', 'agencia'), ('categoria', 'formato'),
                           'titulo',  'cliente', 'parcerias', 'dtinicio', )}),
    )

    tab_materiais = (
        MaterialInline,
    )

    tab_ficha_agencia = (
        (None, {'fields': ('DiretorCriacao','Planejamento', 'Redacao', 'DiretorArte',
                           'ProducaoGrafica', 'ProducaoRTVC')}),
    )

    tab_ficha_fornec = (
        (None,
         {'fields':
              ('ProdutoraFilme','DiretorFilme','ProdutoraAudio','DiretorAudio',
               'EstudioFotografia', 'Fotografo', 'EstudioIlustracao', 'Ilustrador', 'ManipulacaoDigital',
               'Finalizacao',), }),
        ('Outros Fornecedores',
         {'fields': ('OutrosFornecedor1', 'OutrosFornecedor2',
                     'OutrosFornecedor3', 'OutrosFornecedor4',)}),
    )

    tabs = [
        ('Informações Gerais', tab_info),
        ('Quantidade de Materiais', tab_materiais),
        ('Ficha Técnica Agência', tab_ficha_agencia),
        ('Ficha Técnica Fornecedores', tab_ficha_fornec),
    ]

    def get_queryset(self, request):
        qs = super(InscricaoAdmin, self).get_queryset(request)
        if request.user.groups.filter(name='Agência'):
            usuario = Usuario.objects.filter(user=request.user)
            qs = qs.filter(usuario=usuario, premio__status__in=('A','E'))

        return qs

    def get_list_display(self, request):
        if request.user.groups.filter(name='Agência'):
            return 'seq', 'premiacao', 'titulo', 'categoria', 'cliente',
        else:
            return 'empresa', 'seq', 'titulo', 'categoria', 'cliente',

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'empresa':
            if request.user.groups.filter(name='Agência'):
                usuario = Usuario.objects.filter(user=request.user)
                empresas = list(EmpresaUsuario.objects.filter(usuario=usuario).values_list('empresa', flat=True))
                kwargs['queryset'] = Empresa.objects.filter(pk__in=empresas)
            else:
                kwargs['queryset'] = Empresa.objects.all()

            usuario = Usuario.objects.get(user=request.user)
            empresa = EmpresaUsuario.objects.filter(usuario=usuario)

            if empresa.count() == 1:
                kwargs['initial'] = empresa.get().empresa

        elif db_field.name == 'agencia':
            usuario = Usuario.objects.get(user=request.user)
            empresas = EmpresaUsuario.objects.filter(usuario = usuario)
            if empresas.count() == 1:
                agencias = EmpresaAgencia.objects.filter(empresa=empresas.get().empresa)
                if agencias.count() == 1:
                    agencia = EmpresaAgencia.objects.get(empresa=empresas.get().empresa)
                    kwargs['initial'] = agencia
        return super(InscricaoAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        empresa = EmpresaUsuario.objects.get(empresa=request.POST['empresa'])
        obj.usuario = Usuario.objects.get(id=empresa.usuario_id)
        obj.save()
