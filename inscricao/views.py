import cgi
import csv
import datetime
import io
import json
import os
import shutil
import tempfile
import zipfile
from collections import Counter

import requests
from PIL import Image, ImageChops
from bs4 import BeautifulSoup
from django.contrib import messages
from django.contrib.admin.models import LogEntry, ADDITION
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import get_template

from django.views.decorators.csrf import csrf_exempt
from xhtml2pdf.document import pisaDocument

from base.models import Premio, Premiacao, Regional, TipoMaterial
from colunistas import settings
from inscricao.apps import valida_youtube
from inscricao.forms import UsuarioForm
from inscricao.models import Material, Empresa, EmpresaUsuario, Usuario, Inscricao
from util.stdlib import get_model_values, get_model_labels, is_admin
from django.db import models


def tipo_materiais(request, id):
    premiacao = Premiacao.objects.get(id=id)
    context = premiacao.materiais.all().values_list('id', 'descricao', 'arquivo', 'url').order_by('id')

    result = []
    for reg in context:
        result.append({
            'id': reg[0],
            'text': reg[1],
            'arquivo': reg[2],
            'url': reg[3],
        })
    return HttpResponse(json.dumps(result), content_type='application/json')


def dica_materiais(request, id):
    material = TipoMaterial.objects.get(id=id)
    return HttpResponse(json.dumps({'dica': material.dicas}), content_type='application/json')


def dica_materiais_by_name(request, name):
    material = TipoMaterial.objects.get(descricao=name)
    return HttpResponse(json.dumps({'dica': material.dicas}), content_type='application/json')


def filtrar_estados(request, id):
    regional = Regional.objects.get(id=id)
    estados = regional.estados.split(',')
    estados = [estado.strip(' ') for estado in estados]
    return HttpResponse(json.dumps(estados), content_type='application/json')


def get_tipo_materiais(request, id):
    lista_materiais = list(Material.objects.filter(inscricao=id).values('tipo'))
    return HttpResponse(json.dumps(lista_materiais), content_type='application/json')


def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = io.BytesIO()
    pdf = pisaDocument(io.BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None


def exportar_custos(request, *args):

    if request.POST:
        empresa_id = request.POST.get('empresa')
        empresa = Empresa.objects.get(id=empresa_id)
    else:
        empresa = args[0]

    totais = Counter()
    inscricoes = Inscricao.objects.filter(empresa=empresa.pk)
    for inscricao in inscricoes:
        totais[str(inscricao.premiacao)] += 1

    data = {
        'inscricoes': [],
        'logo': 'http://' + request.META['HTTP_HOST'] + '/static/base/img/logo.png'

    }
    for c, v in totais.items():
        data['inscricoes'].append({
            'premiacao': c,
            'qtd': v,
            'valor': 0
        })

    pdf = render_to_pdf('pdf.html', data)
    return HttpResponse(pdf, content_type='application/pdf')


def formularios_custos(request):
    context = {}

    if request.POST:
        empresa_id = request.POST.get('empresa')
        if Empresa.objects.get(id=empresa_id).status != 'A':
            return exportar_custos(request)
        else:
            messages.error(request, 'Esta empresa não está validada')
            return redirect('/')

    else:
        if request.user.is_active:
            usuario = Usuario.objects.filter(user=request.user)
            empresa_usuario = EmpresaUsuario.objects.filter(usuario=usuario)
            if len(empresa_usuario) > 1:
                empresas = list(empresa_usuario.values_list('empresa', 'empresa__nome'))
                empresas_aux = []
                for empresa in empresas:
                    empresas_aux.append({
                        'id': empresa[0],
                        'nome': empresa[1]
                    })
                context['empresas'] = empresas_aux
                return render(request, 'escolher_empresa_exportacao.html', {'context': context})

            elif len(empresa_usuario) == 1:
                if not empresa_usuario.get().status == 'A':
                    return exportar_custos(request, empresa_usuario.get().empresa)
                else:
                    messages.error(request, 'Esta empresa não está validada')
            else:
                messages.error(request, 'Você não tem nenhuma empresa inscrita.')

            return redirect('/')


def inscricoes_cadastradas(request):
    messages.warning(request, 'Rotina ainda não foi implementada.')
    return redirect('/')


def custo_total(empresa):
    total = 0
    inscricoes = Inscricao.objects.filter(empresa=empresa)
    for inscricao in inscricoes:
        total += inscricao.custo()
    return total


def finalizar2(request, *args, **kwargs):
    context = {'finalizar': True}
    if request.POST.get('_send'):
        empresa = Empresa.objects.get(id=request.POST['empresa'])
        empresa.status = 'F'
        empresa.dtfinalizacao = datetime.datetime.now()
        empresa.comprovante = request.FILES.get('comprovante')
        # file = request.FILES.get('comprovante')
        # file_ext = os.path.splitext(file.name)[-1]
        # filename = '%s/%s%s' % (settings.COMPROVANTE_URL, empresa.id, file_ext)
        # default_storage.save(filename, file) # salvando comprovante

        LogEntry.objects.log_action(
            user_id=request.user.pk, content_type_id=ContentType.objects.get_for_model(empresa).pk,
            object_id=empresa.pk,
            object_repr=empresa.serializable_value('nome'),
            action_flag=ADDITION,
            change_message='Finalizada.'
        )
        empresa.save()

        messages.success(request, 'Inscrição Finalizada.')
        return redirect('/')
    else:
        empresa_id = request.POST.get('empresa')
        if empresa_id:
            empresa = Empresa.objects.get(id=empresa_id)
        else:
            empresa = args[0]

        erros = 0
        context['empresa'] = empresa

        total = 0
        for inscricao in empresa.inscricao_set.all():
            if inscricao.status == 'A':
                erros += 1
            else:
                inscricao.preco_final = inscricao.custo()
                inscricao.save()
                total += inscricao.preco_final

        context['custo_total'] = total

        if erros > 0:
            context['finalizar'] = False
            messages.warning(request,
                             'O fechamento não pode seguir adiante pois existem %d inscrições com erro.' % erros)

        return render(request, 'finalizar.html', {'context': context})


@login_required
def finalizar(request):
    context = {}

    if request.POST:
        return finalizar2(request)
    else:
        if request.user.is_active:
            usuario = Usuario.objects.filter(user=request.user)
            empresa_usuario = EmpresaUsuario.objects.filter(usuario=usuario, empresa__status='A')
            if len(empresa_usuario) > 1:
                empresas = list(empresa_usuario.values_list('empresa', 'empresa__nome'))
                empresas_aux = []
                for empresa in empresas:
                    empresas_aux.append({
                        'id': empresa[0],
                        'nome': empresa[1]
                    })
                context['empresas'] = empresas_aux
                return render(request, 'escolher_empresa.html', {'context': context})

            elif len(empresa_usuario) == 1:
                return finalizar2(request, empresa_usuario.get().empresa)

            else:
                if EmpresaUsuario.objects.filter(usuario=usuario, empresa__status='F'):
                    messages.error(request, 'Sua inscrição já foi finalizada. Agora é esperar o resultado!')
                else:
                    messages.error(request, 'Você ainda não tem nenhuma empresa inscrita.')
                return redirect('/')

def create_temporary_copy(material, inscricao):
    extencao = material.arquivo.name.split('/')[1]
    filename = str(inscricao.agencia).upper() + '-' + str((inscricao.titulo).lower()) + '(%s)' % str(material.tipo)[
                                                                                                 :3] + '-' + extencao
    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, filename)
    shutil.copy2(material.arquivo.path, temp_path)
    return temp_path, filename

def empresa_download(request, id):
    empresa = Empresa.objects.get(id=id)
    exclude = ['area', 'regional']
    extras = ['area__descricao', 'regional__nome']

    arquivos_csv = []
    filename = settings.EXPORTACAO + '/empresa%s.csv' % empresa
    arquivos_csv.append(filename)

    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(get_model_labels(empresa, None, exclude, extras))
        writer.writerow(get_model_values(empresa, None, exclude, extras))

    filename = settings.EXPORTACAO + '/inscricao%s.csv' % empresa
    arquivos_csv.append(filename)
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        tot_inscricoes = 0
        for inscricao in Inscricao.objects.filter(empresa=empresa):
            tot_inscricoes += 1
            if tot_inscricoes == 1:
                writer.writerow(get_model_labels(inscricao))
            writer.writerow(get_model_values(inscricao))

    response = HttpResponse(content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename=exportacao_%s.zip' % datetime.datetime.today()
    z = zipfile.ZipFile(response, 'w', zipfile.ZIP_DEFLATED )  ## write zip to response

    for filename in arquivos_csv:
        p = os.path.relpath(os.path.join(filename), os.path.join(filename, '..'))
        z.write(filename, p)

    for incricao in empresa.inscricao_set.all():
        for material in incricao.material_set.all():
            if material.arquivo:
                temporary, filename = create_temporary_copy(material, inscricao)
                z.write(temporary, filename)
    z.close()
    empresa.dtexportacao = datetime.datetime.now()
    empresa.save()
    return response


@csrf_exempt
def salvar_material(request):
    if request.POST:
        tipo = request.POST.get('tipo')
        file = request.FILES.get('file')
        inscricao = request.POST.get('inscricao')
        url = request.POST.get('url')
        id_material = request.POST.get('id_material')
        visualizar = request.POST.get('visualizar')
        mensagens = []

        if tipo and url or file: # se o tipo existe salva
            inscricao_instance = Inscricao.objects.get(id=inscricao)
            tipo = TipoMaterial.objects.get(id=tipo)

            if id_material: #se o material já existir só atualiza
                material = Material.objects.get(id=id_material)
                img_1 = None
                img_2 = None

                if visualizar and material.tipo == tipo and material.url == url and material.arquivo == file: #se nada mudou só retorna os dados
                    resposta = {
                        "mensagens": [],
                        "id": material.id,
                        "url": material.url,
                        "arquivo": material.arquivo.name,
                    }
                    return HttpResponse(json.dumps(resposta), 200)
                else:
                    material.tipo = tipo
                    material.arquivo = file
                    material.url = url
                    material.save()
            else:
                material = Material.objects.create(inscricao=inscricao_instance, tipo=tipo, arquivo=file, url=url)

        else:
            return HttpResponse(json.dumps({"mensagens": mensagens.append({'tipo': 'error', 'msg': 'Insira ao menos o tipo do material e um url ou link'})}))

        #Criticas
        erro = False

        # quantidade de materiais por tipo
        totais = Counter()
        for mat in inscricao_instance.material_set.all():
            if mat:
                totais[str(mat.tipo)] += 1
        erros = []

        # Regra 4
        lista = list(totais.keys())

        # Checagem adicional
        if 'Filme' in lista or 'Videocase' in lista:
            check = False
            for mat in inscricao_instance.material_set.all():
                if material.url and mat.url and not material == mat:
                    if mat.url == material.url:
                        check = True
                        break
            if check:
                erros.append('Não podem haver urls iguais.')

        # Validação de URL
        if not material.url and material.tipo.url:
            erros.append('A URL de %s deve ser informada.' % material.tipo.descricao)

        if material.tipo.descricao == 'Rádio' and material.url is not None:
            request_radio = requests.get(material.url)

            if not request_radio.ok:
                    erros.append(
                        'Link %s inválido. Fonogramas devem estar hospedados no site SoundCloud' %
                        material.url)
            else:
                response_html = BeautifulSoup(request_radio.text, 'html.parser')
                link = response_html.find('link',
                                        attrs={'href': '/sc-opensearch.xml', 'rel': 'search',
                                            'title': 'SoundCloud search',
                                            'type': 'application/opensearchdescription+xml'})
                if not link:
                    erros.append(
                        'Link %s inválido. Fonogramas devem estar hospedados no site SoundCloud' %
                        material.url)

        elif material.tipo.youtube and material.url:
            youtube_error = valida_youtube(material.url)
            if youtube_error:
                erros.append(youtube_error)

        if material.arquivo:
            extension_list = ['.jpg', '.png', '.jpeg', '.gif']
            extension = os.path.splitext(material.arquivo.path)[-1]
            if extension in extension_list:
                image = Image.open(material.arquivo.path)
                try:
                    if image.info['dpi'][0] > 300:
                        erros.append('Imagem inválida, a imagem deve ter menos de 300dpi.')
                        erro = True
                except:
                    None
                if not 'RGB' in image.mode:
                        erros.append(
                            'Imagem inválida (%s). A imagem deve estar no formato RGB.' % image.mode)

                elif image.width >= 3500 or image.height >= 2400:
                    erros.append(
                        'A imagem não pode ter as dimensões maiores que 3500 pixels X 2400 pixels.')

                elif material.arquivo.size > 3145728:
                    erros.append('Imagem inválida: a imagem deve ter até 3 MB.')

        if inscricao_instance.videocase:
            youtube_error = valida_youtube(inscricao_instance.videocase)
            if youtube_error:
                erros.append(youtube_error)

        if len(erros) > 0:
            inscricao_instance.status = 'A'

            mensagens.append({
                "tipo": "warning",
                "msg": "Inscrição foi alterada, mas contém os seguintes erros:",
            })

            for erro in erros:
                mensagens.append({
                "tipo": "error",
                "msg": erro,
            })
            inscricao_instance.save()
            resposta = {
                "mensagens": mensagens,
                "id": material.id,
                "url": material.url,
                "arquivo": material.arquivo.name,
            }

        else:
            if visualizar:
                resposta = {
                    "mensagens": [{'tipo': 'success', 'msg': 'Material alterado com sucesso.'}],
                    "id": material.id,
                    "url": material.url,
                    "arquivo": material.arquivo.name,
                }
            else:
                resposta = {
                        "mensagem": None,
                        "redirect": '/redirect?to=/admin/inscricao/inscricao/%s/change/#tabs-2' % inscricao
                    }
            inscricao_instance.status = 'V'
            inscricao_instance.save()

        return HttpResponse(json.dumps(resposta), 200)


def delete_material(request, pk):
    material = Material.objects.get(id=pk)
    material.delete()
    messages.success(request, 'Material apagado com sucesso.')
    return redirect(request.GET['to'])

def url_redirect(request):
    return redirect(request.GET['to'])

@csrf_exempt
def meus_dados(request):
    if not is_admin(request.user):
        usuario = get_object_or_404(Usuario, user=request.user)
        if request.POST:
            form = UsuarioForm(request.POST, instance=usuario)
            if form.is_valid():
                f = form.save(commit=False)
                f.nome_completo = form.cleaned_data.get('nome_completo')
                user = User.objects.get(id=usuario.user.id)
                user.email = form.cleaned_data.get('email')
                user.save()

                f.save()
                messages.success(request, 'Usuário alterado com sucesso.')
        else:
            form = UsuarioForm(instance=usuario)
        empresas = []
        for emp in usuario.empresausuario_set.all():
            empresas.append({'link': '/admin/inscricao/empresa/%s/change/' %emp.empresa_id, 'nome': emp.empresa})

        return render(request, 'meusdados.html', {'form': form, 'empresas': empresas})
    else:
        raise PermissionDenied


def handler500(request):
    return render(request, '500.html')


def handler404(request):
    return render(request, '404.html')


def handler405(request):
    return render(request, '405.html')

