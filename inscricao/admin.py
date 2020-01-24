import csv
import io
import urllib
import zipfile
import datetime

from collections import Counter

from bs4 import BeautifulSoup

from util.stdlib import upper_first
from django.contrib import admin
from django.http import HttpResponse
from tabbed_admin import TabbedModelAdmin

from base.models import *
from inscricao.models import *

from poweradmin.admin import (PowerButton, PowerModelAdmin, PowerStackedInline,
                              PowerTabularInline)
from django.contrib import messages

from base.views import *

change_form_template = 'admin/myapp/extras/openstreetmap_change_form.html'


class AgenciaInline(admin.TabularInline):
    model = EmpresaAgencia
    fields = ('agencia', 'uf',)
    extra = 0


@admin.register(EmpresaAgencia)
class EmpresaAgenciaAdmin(admin.ModelAdmin):
    list_display = ('agencia', 'empresa', 'uf')

    def get_queryset(self, request):
        qs = super(EmpresaAgenciaAdmin, self).get_queryset(request)
        if request.user.groups.filter(name='Agência'):
            usuario = Usuario.objects.filter(user=request.user)
            empresas = list(EmpresaUsuario.objects.filter(usuario=usuario).values_list('empresa_id', flat=True))
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
    list_filter = ('regional', 'area')
    list_display = ('nome', 'uf', 'cidade', 'area')

    def get_buttons(self, request, object_id):
        buttons = super(EmpresaAdmin, self).get_buttons(request, object_id)
        buttons.append(PowerButton(url='/admin/inscricao/inscricao/add', label=u'Adicionar Inscrição'))
        return buttons

    fieldsets = (
        ('EMPRESA RESPONSÁVEL PELA INSCRIÇÃO', {
            'fields': ('regional', ('nome', 'area'), ('cep', 'cidade', 'uf'), ('endereco', 'bairro'),
                       ('ddd', 'telefone', 'celular'), ('homepage', 'email'))
        }),
        ('VP OU DIRETOR RESPONSÁVEL PELAS INSCRIÇÕES', {
            'fields': (('VP_Nome', 'VP_Cargo'), ('VP_Email', 'VP_DDD', 'VP_Telefone'))
        }),
        (
        'OUTROS CONTATOS NA EMPRESA (Profissionais que também receberão as comunicações da Abracomp sobre a premiação.)',
        {
            'fields': (('C1_Nome', 'C1_Cargo', 'C1_Email', 'C1_DDD', 'C1_Telefone'),
                       ('C2_Nome', 'C2_Cargo', 'C2_Email', 'C2_DDD', 'C2_Telefone',))
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

    def message_user(self, request, message, level=messages.INFO, extra_tags='',
                     fail_silently=False):
        nova_msg = message.split(' ')[3]
        nova_msg = mark_safe('Empresa "<a '+ nova_msg + '</a>" alterada com sucesso.')
        messages.add_message(request, level, nova_msg, extra_tags=extra_tags, fail_silently=fail_silently)

    def get_queryset(self, request):
        qs = super(EmpresaAdmin, self).get_queryset(request)
        if request.user.groups.filter(name='Agência'):
            usuario = Usuario.objects.filter(user=request.user)
            empresas = list(EmpresaUsuario.objects.filter(usuario=usuario).values_list('empresa_id', flat=True))
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

    def save_formset(self, request, form, formset, change):
        duplicidade = 0
        instances = formset.save(commit=False)
        existentes = formset.cleaned_data
        for instance in instances:
            for agencia in existentes:
                if instance.agencia == agencia['agencia']:
                    duplicidade += 1
            if duplicidade < 2:
                instance.save()
                formset.save_m2m()
            else:
                messages.warning(request, 'Não é permitido agências com mesmo nome. A agência duplicada foi excluída')

        for obj in formset.deleted_objects:
            obj.delete()


class MaterialInline(admin.TabularInline):
    model = Material
    fields = ('tipo', 'arquivo', 'url',)
    extra = 1

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.premio:
            if obj.premio.status == 'F':
                return list(super().get_fields(request, obj))
        return super(MaterialInline, self).get_readonly_fields(request, obj)


class AnoFilter(admin.SimpleListFilter):
    title = 'ano'
    parameter_name = 'ano'

    def lookups(self, request, model_admin):
        if request.user.is_superuser:
            q = Premio.objects.values('ano').distinct().order_by('ano')
            regs = []
            for ano in q:
                regs.append((ano['ano'], ano['ano']))
            return tuple(regs)

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            return queryset.filter(premio__ano=value)


class RegionalFilter(admin.SimpleListFilter):
    title = 'regional'
    parameter_name = 'regional'

    def lookups(self, request, model_admin):
        if request.user.is_superuser:
            regionais = Regional.objects.values('nome', 'id').all()
            regs = []
            for reg in regionais:
                regs.append((reg['id'], reg['nome']))
            return tuple(regs)
        else:
            usuario = Usuario.objects.filter(user=request.user)
            inscricoes = Inscricao.objects.filter(usuario=usuario)
            reg_disponiveis = []
            for ins in inscricoes:
                if ins.premio:
                    reg_disponiveis.append((ins.premio.regional.id, ins.premio.regional))
            return tuple(reg_disponiveis)

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            return queryset.filter(premio__regional=value)
        else:
            return queryset.all()


@admin.register(Inscricao)
class InscricaoAdmin(PowerModelAdmin, TabbedModelAdmin):
    list_filter = ('premiacao', RegionalFilter, AnoFilter)
    readonly_fields = ('seq',)
    tab_info = (
        (None, {'fields': (('premiacao', 'empresa', 'agencia',), 'categoria',
                           'titulo', 'cliente', 'parcerias', 'produto', 'dtinicio',)}),
    )

    tab_materiais = (
        MaterialInline,
    )

    tab_ficha_agencia = (
        (None, {'fields': ('DiretorCriacao', 'Planejamento', 'Redacao', 'DiretorArte',
                           'ProducaoGrafica', 'ProducaoRTVC', 'TecnologiaDigital',
                           'Midia', 'Atendimento', 'Aprovacao',
                           'OutrosAgencia1', 'OutrosAgencia2',
                           'OutrosAgencia3', 'OutrosAgencia4', )}),
    )

    tab_ficha_fornec = (
        (None,
         {'fields':
              ('ProdutoraFilme', 'DiretorFilme', 'ProdutoraAudio', 'DiretorAudio',
               'EstudioFotografia', 'Fotografo', 'EstudioIlustracao', 'Ilustrador', 'ManipulacaoDigital',
               'Finalizacao',), }),
        ('Outros Fornecedores',
         {'fields': ('OutrosFornecedor1', 'OutrosFornecedor2',
                     'OutrosFornecedor3', 'OutrosFornecedor4',)}),
    )

    tabs = [
        (u'Informações Gerais', tab_info),
        (u'Quantidade de Materiais', tab_materiais),
        (u'Ficha Técnica Agência', tab_ficha_agencia),
        (u'Ficha Técnica Fornecedores', tab_ficha_fornec),
    ]

    tab_info = [
        ('Informações Gerais', tab_info)
    ]
    actions = ('exportar',)

    change_form_template = 'admin/inscricao/inscricao/change_form.html'

    def get_tabs(self, request, obj=None):
        if not obj:
            return self.tab_info
        return self.tabs

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.premio:
            if obj.premio.status == 'F':
                return ('premiacao','usuario','empresa','seq','titulo','agencia','categoria','cliente','parcerias',
                        'produto','dtinicio','isolada','DiretorCriacao','Planejamento','Redacao','DiretorArte',
                        'ProducaoGrafica','ProducaoRTVC','TecnologiaDigital','OutrosAgencia1','OutrosAgencia2',
                        'OutrosAgencia3','OutrosAgencia4','Midia','Atendimento','Aprovacao','ProdutoraFilme',
                        'DiretorFilme','ProdutoraAudio','DiretorAudio', 'EstudioFotografia','Fotografo',
                        'EstudioIlustracao','Ilustrador','ManipulacaoDigital','Finalizacao','OutrosFornecedor1',
                        'OutrosFornecedor2','OutrosFornecedor3','OutrosFornecedor4','dtinclusao','dtexportacao',)
        return super(InscricaoAdmin, self).get_readonly_fields(request, obj)

    def get_queryset(self, request):
        qs = super(InscricaoAdmin, self).get_queryset(request)
        if request.user.groups.filter(name='Agência'):
            usuario = Usuario.objects.filter(user=request.user)
            qs = qs.filter(usuario=usuario, premio__status__in=('A', 'E'))

        return qs

    def get_list_display(self, request):
        if request.user.groups.filter(name='Agência'):
            return 'titulo', 'seq', 'premiacao', 'categoria', 'cliente', 'status'
        else:
            return 'empresa', 'seq', 'titulo', 'categoria', 'cliente', 'status'

    def get_actions(self, request):
        actions = super(InscricaoAdmin, self).get_actions(request)
        del actions['export_as_csv']
        if not request.user.is_superuser:
            del actions['exportar']
        return actions

    def gravar_inscricoes(self, queryset, lista_empresas):
        output = io.StringIO()  # temp output file
        writer = csv.writer(output, dialect='excel', delimiter=';')
        for query in queryset:
            writer.writerow([
                query.id,
                query.premiacao,
                query.premio.regional,
                query.premio.ano,
                query.empresa.id,
                query.empresa,
                query.seq,
                query.titulo,
                query.agencia.id,
                query.agencia,
                query.categoria.codigo,
                query.cliente,
                query.parcerias,
                query.produto,
                query.dtinicio,
                query.isolada,
                query.DiretorCriacao,
                query.Planejamento,
                query.Redacao,
                query.DiretorArte,
                query.ProducaoGrafica,
                query.ProducaoRTVC,
                query.TecnologiaDigital,
                query.OutrosAgencia1,
                query.OutrosAgencia2,
                query.OutrosAgencia3,
                query.OutrosAgencia4,
                query.Midia,
                query.Atendimento,
                query.Aprovacao,
                query.ProdutoraFilme,
                query.DiretorFilme,
                query.ProdutoraAudio,
                query.DiretorAudio,
                query.EstudioFotografia,
                query.Fotografo,
                query.EstudioIlustracao,
                query.Ilustrador,
                query.ManipulacaoDigital,
                query.Finalizacao,
                query.OutrosFornecedor1,
                query.OutrosFornecedor2,
                query.OutrosFornecedor3,
                query.OutrosFornecedor4,
            ])
            if query.empresa not in lista_empresas:
                lista_empresas.append(query.empresa)
        return output

    def gravar_materiais(self, queryset):
        output = io.StringIO()
        writer = csv.writer(output, dialect='excel', delimiter=';')
        writer.writerow(['Inscricao', 'Tipo', 'Arquivo', 'URL', 'IDSoundCloud'])
        for query in queryset:
            for mat in query.material_set.all():
                writer.writerow([mat.inscricao_id, mat.tipo_id, mat.arquivo, mat.url, mat.idsoundcloud])
        return output

    def gravar_empresas(self, queryset, lista_empresas):
        output = io.StringIO()
        writer = csv.writer(output, dialect='excel', delimiter=';')
        writer.writerow(['Nome'])
        for query in lista_empresas:
            writer.writerow([query])
        return output

    def exportar(self, request, queryset):

        response = HttpResponse(content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename=backup %s.zip' % datetime.date.today()
        z = zipfile.ZipFile(response, 'w')  ## write zip to response
        lista_empresas = []

        # criando zip
        inscricoes = self.gravar_inscricoes(queryset, lista_empresas)
        z.writestr("inscricoes.csv", inscricoes.getvalue())
        materiais = self.gravar_materiais(queryset)
        z.writestr("materiais.csv", materiais.getvalue())
        empresa = self.gravar_empresas(queryset, lista_empresas)
        z.writestr("empresas.csv", empresa.getvalue())

        for inscricao in queryset:
            inscricao.dtexportacao = datetime.date.today()
        return response

    exportar.short_description = u'Exportação das Inscrições'

    # retorna uma lista de ids de empresas válidas
    def empresas_validas(self, user):
        if user.groups.filter(name='Agência'):
            usuario = Usuario.objects.filter(user=user)
            candidatas = EmpresaUsuario.objects.filter(usuario=usuario)
            empresas = []
            for empresa in candidatas:
                if Premio.objects.filter(regional=empresa.empresa.regional, status='A').count() > 0:
                    empresas.append(empresa.empresa_id)
        else:
            regionais_ativas = Premio.objects.filter(status='A').values_list('regional')
            empresas = list(Empresa.objects.filter(regional__in=regionais_ativas).values_list('id', flat=True))
        return empresas

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'empresa':
            empresas = self.empresas_validas(request.user)
            kwargs['queryset'] = Empresa.objects.filter(pk__in=empresas)

            if len(empresas) == 1:
                kwargs['initial'] = Empresa.objects.get(id=empresas[0])

        elif db_field.name == 'agencia':
            empresas = self.empresas_validas(request.user)
            if len(empresas) == 1:
                agencias = EmpresaAgencia.objects.filter(empresa=empresas[0])
                if agencias.count() == 1:
                    kwargs['initial'] = agencias[0]

        return super(InscricaoAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def message_user(self, request, message, level=messages.INFO, extra_tags='',
                     fail_silently=False):
        nova_msg = message.split(' ')[3]
        nova_msg = mark_safe('Inscrição "<a '+ nova_msg + ' alterada com sucesso.')
        messages.add_message(request, level, nova_msg, extra_tags=extra_tags, fail_silently=fail_silently)

    def get_form(self, request, obj=None, **kwargs):
        texto_outros_autores = 'Utilize o formato: "Função, Fulano, Beltrano e Sicrano'

        form = super(InscricaoAdmin, self).get_form(request, obj, **kwargs)
        try:
            form.base_fields['DiretorCriacao'].widget.attrs['placeholder'] = texto_outros_autores
            form.base_fields['OutrosAgencia1'].widget.attrs['placeholder'] = texto_outros_autores
            form.base_fields['OutrosAgencia2'].widget.attrs['placeholder'] = texto_outros_autores
            form.base_fields['OutrosAgencia3'].widget.attrs['placeholder'] = texto_outros_autores
            form.base_fields['OutrosAgencia4'].widget.attrs['placeholder'] = texto_outros_autores
            form.base_fields['OutrosFornecedor1'].widget.attrs['placeholder'] = texto_outros_autores
            form.base_fields['OutrosFornecedor2'].widget.attrs['placeholder'] = texto_outros_autores
            form.base_fields['OutrosFornecedor3'].widget.attrs['placeholder'] = texto_outros_autores
            form.base_fields['OutrosFornecedor4'].widget.attrs['placeholder'] = texto_outros_autores
        except Exception:
            None
        return form

    def save_model(self, request, obj, form, change):
        obj.titulo = upper_first(obj.titulo)
        obj.parcerias = upper_first(obj.parcerias)
        obj.cliente = upper_first(obj.cliente)
        obj.produto = upper_first(obj.produto)
        obj.DiretorCriacao = upper_first(obj.DiretorCriacao)
        obj.Planejamento = upper_first(obj.Planejamento)
        obj.Redacao = upper_first(obj.Redacao)
        obj.DiretorArte = upper_first(obj.DiretorArte)
        obj.ProducaoGrafica = upper_first(obj.ProducaoGrafica)
        obj.ProducaoRTVC = upper_first(obj.ProducaoRTVC)
        obj.TecnologiaDigital = upper_first(obj.TecnologiaDigital)
        obj.OutrosAgencia1 = upper_first(obj.OutrosAgencia1)
        obj.OutrosAgencia2 = upper_first(obj.OutrosAgencia2)
        obj.OutrosAgencia3 = upper_first(obj.OutrosAgencia3)
        obj.OutrosAgencia4 = upper_first(obj.OutrosAgencia4)
        obj.Midia = upper_first(obj.Midia)
        obj.Atendimento = upper_first(obj.Atendimento)
        obj.Aprovacao = upper_first(obj.Aprovacao)
        obj.ProdutoraFilme = upper_first(obj.ProdutoraFilme)
        obj.DiretorFilme = upper_first(obj.DiretorFilme)
        obj.ProdutoraAudio = upper_first(obj.ProdutoraAudio)
        obj.DiretorAudio = upper_first(obj.DiretorAudio)
        obj.EstudioFotografia = upper_first(obj.EstudioFotografia)
        obj.Fotografo = upper_first(obj.Fotografo)
        obj.EstudioIlustracao = upper_first(obj.EstudioIlustracao)
        obj.Ilustrador = upper_first(obj.Ilustrador)
        obj.ManipulacaoDigital = upper_first(obj.ManipulacaoDigital)
        obj.Finalizacao = upper_first(obj.Finalizacao)
        obj.OutrosFornecedor1 = upper_first(obj.OutrosFornecedor1)
        obj.OutrosFornecedor2 = upper_first(obj.OutrosFornecedor2)
        obj.OutrosFornecedor3 = upper_first(obj.OutrosFornecedor3)
        obj.OutrosFornecedor4 = upper_first(obj.OutrosFornecedor4)

        if ',' in obj.titulo or '/' in obj.titulo:
            messages.warning(request, 'Não coloque os títulos de cada peça. Use um título que identifique o conjunto')

        if obj.produto:
            if 'institucional' in obj.produto.lower() and 'institucional' not in obj.categoria.nome.lower():
                messages.warning(request,
                                 "Esta inscrição não está na categoria Institucional. " +
                                 "Indique um produto mais preciso ou deixe o campo em branco")

        if obj.cliente == obj.produto and obj.cliente:
            obj.produto = ''
            messages.info(request,
                          "Se o campo Produto tiver a mesma informação do campo Cliente não há necessidade de preenchimento!")

        empresa = Empresa.objects.get(id=request.POST['empresa'])

        if not obj.usuario:
            usuario = EmpresaUsuario.objects.filter(empresa=empresa)[0]
            obj.usuario = Usuario.objects.get(id=usuario.usuario_id)

        if not obj.premio:
            regional = Regional.objects.get(id=empresa.regional.id)
            try:
                obj.premio = Premio.objects.get(regional=regional, status='A')
            except Premio.MultipleObjectsReturned:
                messages.error(request,
                          "Existe mais de um prêmio ativo para a regional %s" % regional)
                obj.status = 'A'
            except Premio.DoesNotExist:
                messages.error(request,
                          "Não existe nenhuma premiação ativa para a regional %s" % regional)
                obj.status = 'A'
        obj.save()

    def save_formset(self, request, form, formset, change):
        warn1 = False
        warn2 = False

        # quantidade de materiais por tipo
        totais = Counter()
        for mat in formset.cleaned_data:
            if mat:
                totais[ mat['tipo'].descricao ] += 1

        # Regra 1
        regra1 = False
        codigo = form.cleaned_data['categoria'].codigo
        for categoria in ('BRD10', 'MID10', 'RPB10', 'DES10', 'PRM10', 'PRM20', 'PRM30'):
            if categoria in codigo:
                regra1 = True
                break

        # Se for um dos prefixos acima, deve haver pelo menos uma apresentação ou videocase
        if regra1:
            if totais['Apresentação'] + totais['Video Case'] < 1:
                messages.warning(request,
                                 "Nesta Área e nesta Categoria é obrigatório apresentar uma apresentação (como PPT) ou um videocase. Veja no site em ‘Como preparar os seus materiais'.")
                warn1 = True

        if form.cleaned_data['premiacao'].codigo == 'FIL':
            if totais['10'] + totais['9'] >= 1:
                messages.warning(request,
                                 "Nesta Área e nesta Categoria, não basta apresentar o videocase ou a apresentação. Indique a quantidade e o tipo de peça referente ao trabalho")
                warn2 = True
        # Regra 3
        if 'INT1' in codigo:
            if len(totais.keys()) < 2:
                messages.warning(request, 'Deve haver pelo menos 2 tipos de materiais diferentes para esta categoria.')

        # Regra 4
        lista = list(totais.keys())
        if 'BRC101' == codigo or 'BRC103' == codigo:
            if not 'Filme' in lista:
                messages.warning(request, 'O Tipo de material "Filme" é obrigatório para essa categoria.')

        elif 'BRC102' == codigo or 'BRC104' == codigo:
            if 'Mídia Digital' not in lista and 'Filme' not in lista:
                messages.warning(request,
                                 'Os Tipos de materiais "Filme ou Mídias Digitais" são obrigatórios para essa categoria.')
        elif 'BRC105' == codigo:
            if 'Jornal' not in lista and 'Revista' not in lista:
                messages.warning(request,
                                 'Os Tipos de materiais "Jornal ou Revista" são obrigatórios para essa categoria.')

        # Regra 5
        if form.cleaned_data['premiacao'].codigo == 'IMP':
            for imp in range(100, 200+1):
                c = 'IMP%d' % imp
                if c in codigo:
                    if 'Jornal' not in lista or 'Revista' not in lista:
                        messages.warning(request, 'É obrigatório ter os materiais Jornal e Revista para essa categoria.')
                    break
        #Regra 7
        if 'DIG30' in codigo:
            if 'Web Sites' not in lista or len(lista) > 1:
                messages.warning(request, 'É obrigatório ter somente o material Web Sites para essa categoria.')

        elif 'DIG1' in codigo:
            if 'Peças de Design' not in lista or len(lista) > 1:  # Obs: No doc está peças digitais, não encontrei e coloquei esse.
                messages.warning(request, 'É obrigatório ter somente o material Peças de Design para essa categoria.')


        # Regra 8
        if 'FIL1' in codigo or 'FIL20' in codigo:
            if 'Filme' not in lista:
                messages.warning(request, 'É obrigatório ter o material Filme para essa categoria.')

        # Regra 9
        if 'DIR201' == codigo:
            if 'Filme' not in lista and 'Rádio' not in lista: #Se nenhum dois dois estiver na lista
                messages.warning(request, 'É obrigatório ter um dos materiais Filme ou Rádio para essa categoria.')

        elif 'DIR202' == codigo:
            if 'Jornal' not in lista and 'Revista' not in lista and 'Promo' not in lista: #Se nenhum dois três estiver na lista
                messages.warning(request, 'É obrigatório ter um materiais de Jornal, Revista e Promo para essa categoria.')

        elif 'DIR203' == codigo:
            if 'Digital' not in lista:
                messages.warning(request, 'É obrigatório ter o material Digital para essa categoria.')

        elif 'DIR204' == codigo or 'DIR205' == codigo:
            if 'Promo' not in lista:
                messages.warning(request, 'É obrigatório ter o material Promo para essa categoria.')

        elif 'DIR206' == codigo:
            if 'Digital' not in lista and 'Web Sites' not in lista and 'Promo' not in lista:
                messages.warning(request, 'É obrigatório ter um desses materiais "Digital, Web Sites ou Promo," para essa categoria.')

        elif 'DIR207' == codigo:
            if 'Promo' not in lista:
                messages.warning(request, 'É obrigatório ter o material Promo para essa categoria.')

        #Regra 10
        if 'MID101' == codigo or 'MID102' == codigo:
            if 'Filme' not in lista:
                messages.warning(request, 'É obrigatório ter o material Filme para essa categoria.')

        elif 'MID103' == codigo:
            if 'Rádio' not in lista:
                messages.warning(request, 'É obrigatório ter o material Rádio para essa categoria.')

        elif 'MID104' == codigo:
            if 'Jornal' not in lista:
                messages.warning(request, 'É obrigatório ter o material Jornal para essa categoria.')

        elif 'MID105' == codigo:
            if 'Revista' not in lista:
                messages.warning(request, 'É obrigatório ter o material Revista para essa categoria.')

        elif 'MID106' == codigo:
            if 'Exterior' not in lista:
                messages.warning(request, 'É obrigatório ter o material Exterior para essa categoria.')

        elif 'MID107' == codigo or 'MID108' == codigo:
            if 'Digital' not in lista:
                messages.warning(request, 'É obrigatório ter o material Digital para essa categoria.')

        # Regra 11
        if 'EXT1' in codigo or 'EXT20' in codigo:
            if 'Exterior' not in lista:
                messages.warning(request, 'É obrigatório ter o material Exterior para essa categoria.')

        # Regra 13
        if 'PRM1' in codigo or 'PRM2' in codigo or 'PRM3' in codigo:
            if 'Promo' not in lista:
                messages.warning(request, 'É obrigatório ter o material Promo para essa categoria.')

        elif 'PRM404' == codigo:
            if 'Web Sites' not in lista and 'Digital' not in lista:
                messages.warning(request, 'É obrigatório ter o um dos desses materiais Web Sites, Digital para essa categoria.')

        elif 'PRM4' in codigo:
            if 'Promo' not in lista:
                messages.warning(request, 'É obrigatório ter o material Promo para essa categoria.')

        elif 'RAD1' in codigo or 'RAD20' in codigo:
            if 'Rádio' not in lista:
                messages.warning(request, 'É obrigatório ter o material Rádio para essa categoria.')

        # Regra 16
        if 'TEC10' in codigo:
            if 'Filme' not in lista:
                messages.warning(request, 'É obrigatório ter o material Filme para essa categoria.')

        elif 'TEC206' == codigo:
            if 'Rádio' not in lista and 'Filme' not in lista:
                messages.warning(request, 'É obrigatório ter o material Rádio ou Filme para essa categoria.')

        elif 'TEC201' == codigo or 'TEC202' == codigo or 'TEC204' == codigo:
            if 'Rádio' not in lista:
                messages.warning(request, 'É obrigatório ter o material Rádio para essa categoria.')

        elif 'TEC203' == codigo or 'TEC205' == codigo or 'TEC206' == codigo:
            if 'Filme' not in lista:
                messages.warning(request, 'É obrigatório ter o material Filme para essa categoria.')

        elif 'TEC30' in codigo:
            if 'Jornal' not in lista and 'Revista' not in lista and 'Exterior' not in lista and 'Promo' not in lista:
                messages.warning(request, 'É obrigatório ter o um dos desses materiais  Jornal, Revista, Exterior ou Promo para essa categoria.')

        # Checagem adicional
        if 'Filme' in lista or 'Videocase' in lista:
            check = False
            url = ''
            for mat in formset.cleaned_data:
                if not mat.get('url', False) == url:
                    url = mat.get('url', False)
                else:
                    check = True
                    break
            if check:
                messages.warning(request, 'Não pode ter urls iguais.')

        # Validação dos URL´s
        import requests
        instances = formset.save(commit=False)
        for instance in instances:
            if instance.url:
                url = instance.url.split('//')
                if 'www' in url[1]:
                    url = url[1].split('.')
                    url = url[1] + '.' + url[2]
                else:
                    url = url[1]

                r = requests.get('http://' + url)
                if not r.ok:
                    messages.error(request, 'Link inválido. O vídeo não existe no servidor especificado.')
                else:
                    soup = BeautifulSoup(r.content, 'html.parser')
                    title = soup.title.text
                    if title == 'YouTube':
                        messages.error(request, 'Link inválido. O vídeo não existe no servidor especificado.')

                url = url.split('/')[0]
                if not 'youtube.com' == url and not 'youtu.be' == url and not 'vimeo.com' == url:
                    messages.error(request, 'O filme ou vídeo deve estar hospedado no YouTube ou no Vimeo!')

        if not warn1 and not warn2:
            form.instance.status = 'V'
        else:
            form.instance.status = 'A'
        form.save()
        formset.save()
