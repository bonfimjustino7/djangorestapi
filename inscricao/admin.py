from django.contrib import admin

from poweradmin.admin import PowerModelAdmin, PowerButton, PowerStackedInline, PowerTabularInline
from tabbed_admin import TabbedModelAdmin

from base.models import *
from inscricao.models import *


class AgenciaInline(admin.TabularInline):
    model = EmpresaAgencia
    fields = ('agencia', 'uf', )
    extra = 0


@admin.register(EmpresaUsuario)
class EmpresaUsuarioAdmin(admin.ModelAdmin):
    list_display = ('empresa', 'usuario')


@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_filter = ('regional','area')
    list_display = ('nome', 'uf', 'municipio','area')
    fields = (('nome', 'regional', 'area',), ('cep', 'uf', 'municipio'),
              ('endereco', 'bairro'), ('ddd', 'telefone', 'celular'),
              ('homepage', 'email'),
              ('VP_Nome', 'VP_Cargo', 'VP_Email'), ('VP_DDD', 'VP_Telefone',),
              ('C1_Nome', 'C1_Cargo', 'C1_Email'), ('C1_DDD', 'C1_Telefone',),
              ('C2_Nome', 'C2_Cargo', 'C2_Email'), ('C2_DDD', 'C2_Telefone',),
              )
    inlines = [AgenciaInline]

    def get_form(self, request, obj=None, **kwargs):
        form = super(EmpresaAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['cep'].widget.attrs['style'] = 'width: 5em;'
        form.base_fields['nome'].widget.attrs['style'] = 'width: 30em;'
        form.base_fields['endereco'].widget.attrs['style'] = 'width: 30em;'
        form.base_fields['bairro'].widget.attrs['style'] = 'width: 20em;'
        form.base_fields['ddd'].widget.attrs['style'] = 'width: 2em;'
        form.base_fields['VP_DDD'].widget.attrs['style'] = 'width: 2em;'
        form.base_fields['C1_DDD'].widget.attrs['style'] = 'width: 2em;'
        form.base_fields['C2_DDD'].widget.attrs['style'] = 'width: 2em;'
        form.base_fields['telefone'].widget.attrs['style'] = 'width: 10em;'
        form.base_fields['VP_Telefone'].widget.attrs['style'] = 'width: 10em;'
        form.base_fields['C1_Telefone'].widget.attrs['style'] = 'width: 10em;'
        form.base_fields['C2_Telefone'].widget.attrs['style'] = 'width: 10em;'
        return form

    def get_queryset(self, request):
        qs = super(EmpresaAdmin, self).get_queryset(request)
        if request.user.groups.filter(name='Agência'):
            usuario = Usuario.objects.filter(user=request.user)
            empresas = list(EmpresaUsuario.objects.filter(usuario = usuario).values_list('empresa_id', flat=True))
            qs = qs.filter(pk__in=empresas)

        return qs


class MaterialInline(admin.TabularInline):
    model = Material
    fields = ('tipo', 'arquivo', 'url', )


@admin.register(Inscricao)
class InscricaoAdmin(PowerModelAdmin, TabbedModelAdmin):
    list_filter = ('premio', )
    list_display = ('empresa', 'seq', 'titulo', 'categoria', 'cliente')

    tab_info = (
        (None, {'fields': ('premio', 'empresa', 'titulo', 'categoria', 'cliente')}),
    )

    tab_materiais = (
        MaterialInline,
    )

    tab_ficha_agencia = (
        (None, {'fields': ('DiretorCriacao','Planejamento', 'Redacao', 'DiretorArte',
                           'ProducaoGrafica', 'ProducaoRTVC')}),
    )

    tab_ficha_fornec = (
        (None, {'fields': ('ProdutoraFilme','DiretorFilme','ProdutoraAudio','DiretorAudio')}),
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

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'empresa':
            if request.user.groups.filter(name='Agência'):
                usuario = Usuario.objects.filter(user=request.user)
                empresas = list(EmpresaUsuario.objects.filter(usuario=usuario).values_list('empresa', flat=True))
                kwargs['queryset'] = Empresa.objects.filter(pk__in=empresas)
            else:
                kwargs['queryset'] = Empresa.objects.all()

        return super(InscricaoAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


admin.site.register(Usuario)
