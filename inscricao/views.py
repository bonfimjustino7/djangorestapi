import csv
import io
import json
import os
import zipfile
from collections import Counter
from datetime import datetime

import requests
from PIL import Image, ImageChops
from bs4 import BeautifulSoup
from django.contrib import messages
from django.contrib.admin.utils import label_for_field, lookup_field, display_for_value, display_for_field
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils.html import strip_tags
from django.views.decorators.csrf import csrf_exempt

from base.models import Premio, Premiacao, Regional, TipoMaterial
from colunistas import settings
from inscricao.apps import valida_youtube
from inscricao.models import Material, Empresa, EmpresaUsuario, Usuario, Inscricao
from util.stdlib import get_model_values, get_model_labels
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


def formularios_custos(request):
    messages.warning(request, 'Rotina ainda não foi implementada.')
    return redirect('/')


def inscricoes_cadastradas(request):
    messages.warning(request, 'Rotina ainda não foi implementada.')
    return redirect('/')


def custos_total(empresa):
    total = 0
    inscricoes = Inscricao.objects.filter(empresa=empresa)
    for inscricao in inscricoes:
        total += inscricao.material_set.all().count() * 100

    return total


def finalizar2(request, *args, **kwargs):
    context = {'finalizar': True}
    if request.POST.get('_send'):
        file = request.FILES.get('comprovante')
        filename = settings.COMPROVANTE_URL + '/' + file.name
        default_storage.save(filename, file) # salvando comprovante
        empresa = Empresa.objects.get(id=request.POST['empresa'])
        empresa.status = 'F'
        empresa.dtfinalizacao = datetime.now()
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
        context['custo_total'] = '%.2f' % float(custos_total(empresa))
        for inscricao in empresa.inscricao_set.all():
            if inscricao.status == 'A':
                erros += 1

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
                messages.error(request, 'Você não tem nenhuma empresa inscrita.')
                return redirect('/')


def empresa_download(request, id):
    empresa = Empresa.objects.get(id=id)
    path = settings.EXPORTACAO + '/%s_2020.csv' % empresa
    exclude = ['area', 'regional']
    extras = ['area__descricao', 'regional__nome']

    if not os.path.exists(path):
        with open(path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(get_model_labels(empresa, None, exclude, extras))
            writer.writerow(get_model_values(empresa, None, exclude, extras))

    response = HttpResponse(content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename=exportacao_%s.zip' % datetime.today()
    z = zipfile.ZipFile(response, 'w', zipfile.ZIP_DEFLATED )  ## write zip to response
    p = os.path.relpath(os.path.join(path), os.path.join(path, '..'))
    z.write(path, p)
    for incricao in empresa.inscricao_set.all():
        for material in incricao.material_set.all():
            if material.arquivo:
                caminho = os.path.relpath(os.path.join(material.arquivo.path), os.path.join(material.arquivo.path, '..'))
                z.write(material.arquivo.path, caminho)
    z.close()
    empresa.dtexportacao = datetime.now()
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
                    messages.success(request, 'Material alterado com sucesso.')
            else:
                material = Material.objects.create(inscricao=inscricao_instance, tipo=tipo, arquivo=file, url=url)
                messages.success(request, 'Material criado com sucesso.')
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

        # Regra 1
        regra1 = False
        codigo = inscricao_instance.categoria.codigo
        for categoria in ('BRD10', 'MID10', 'RPB10', 'DES10', 'PRM10', 'PRM20', 'PRM30'):
            if categoria in codigo:
                regra1 = True
                break

        if regra1:
            if not inscricao_instance.videocase and not inscricao_instance.apresentacao:
                erros.append(
                     "Nesta Área e nesta Categoria é obrigatório incluir uma apresentação (como PPT) ou um videocase. "
                     "Veja no site em ‘Como preparar os seus materiais'.")

        # regra 2
        if inscricao_instance.premiacao.codigo == 'FIL':
            if totais['10'] + totais['9'] >= 1:
                erros.append(
                    "Nesta Área e nesta Categoria, não basta apresentar o videocase ou a apresentação. "
                    "Indique a quantidade e o tipo de peça referente ao trabalho")

            # Regra 3
        if 'INT1' in codigo:
            if len(totais.keys()) < 2:
                erros.append('Deve haver pelo menos 2 tipos de materiais diferentes para esta categoria.')

            # Regra 4
        lista = list(totais.keys())
        if 'BRC101' == codigo or 'BRC103' == codigo:
            if 'Filme' not in lista:
                erros.append('O Tipo de material "Filme" é obrigatório para essa categoria.')

        elif 'BRC102' == codigo or 'BRC104' == codigo:
            if 'Mídia Digital' not in lista and 'Filme' not in lista:
                erros.append(
                    'Os Tipos de materiais "Filme ou Mídias Digitais" são obrigatórios para essa categoria.')

        elif 'BRC105' == codigo:
            if 'Jornal' not in lista and 'Revista' not in lista:
                erros.append('Os Tipos de materiais "Jornal ou Revista" são obrigatórios para essa categoria.')

        # Regra 5
        if inscricao_instance.premiacao.codigo == 'IMP':
            for imp in range(100, 200 + 1):
                c = 'IMP%d' % imp
                if c in codigo:
                    if 'Jornal' not in lista or 'Revista' not in lista:
                        erros.append('É obrigatório ter os materiais Jornal e Revista para essa categoria.')
                    break

        # Regra 7
        if 'DIG30' in codigo:
            if 'Web Sites' not in lista or len(lista) > 1:
                erros.append('É obrigatório ter somente Web Sites para essa categoria.')

        elif 'DIG1' in codigo:
            if 'Mídia Digital' not in lista:
                erros.append('É obrigatório ter somente Mídias Digitais para essa categoria.')

        # Regra 8
        if 'FIL1' in codigo or 'FIL20' in codigo:
            if 'Filme' not in lista:
                erros.append('É obrigatório ter o material Filme para essa categoria.')

        # Regra 9
        if 'DIR201' == codigo:
            if 'Filme' not in lista and 'Rádio' not in lista:  # Se nenhum dois dois estiver na lista
                erros.append('É obrigatório ter um dos materiais Filme ou Rádio para essa categoria.')

        elif 'DIR202' == codigo:
            if 'Jornal' not in lista and 'Revista' not in lista and 'Promo' not in lista:  # Se nenhum dois três estiver na lista
                erros.append('É obrigatório ter um materiais de Jornal, Revista e Promo para essa categoria.')

        elif 'DIR203' == codigo:
            if 'Digital' not in lista:
                erros.append('É obrigatório ter o material Digital para essa categoria.')

        elif 'DIR204' == codigo or 'DIR205' == codigo:
            if 'Promo' not in lista:
                erros.append('É obrigatório ter o material Promo para essa categoria.')

        elif 'DIR206' == codigo:
            if 'Digital' not in lista and 'Web Sites' not in lista and 'Promo' not in lista:
                erros.append(
                    'É obrigatório ter um desses materiais "Digital, Web Sites ou Promo" para essa categoria.')

        elif 'DIR207' == codigo:
            if 'Promo' not in lista:
                erros.append('É obrigatório ter o material Promo para essa categoria.')

        # Regra 10
        if 'MID101' == codigo or 'MID102' == codigo:
            if 'Filme' not in lista:
                erros.append('É obrigatório ter o material Filme para essa categoria.')

        elif 'MID103' == codigo:
            if 'Rádio' not in lista:
                erros.append('É obrigatório ter o material Rádio para essa categoria.')

        elif 'MID104' == codigo:
            if 'Jornal' not in lista:
                erros.append('É obrigatório ter o material Jornal para essa categoria.')

        elif 'MID105' == codigo:
            if 'Revista' not in lista:
                erros.append('É obrigatório ter o material Revista para essa categoria.')

        elif 'MID106' == codigo:
            if 'Exterior' not in lista:
                erros.append('É obrigatório ter o material Exterior para essa categoria.')

        elif 'MID107' == codigo or 'MID108' == codigo:
            if 'Digital' not in lista:
                erros.append('É obrigatório ter o material Digital para essa categoria.')

        # Regra 11
        if 'EXT1' in codigo or 'EXT20' in codigo:
            if 'Exterior' not in lista:
                erros.append('É obrigatório ter o material Exterior para essa categoria.')

        # Regra 13
        if 'PRM1' in codigo or 'PRM2' in codigo or 'PRM3' in codigo:
            if 'Promo' not in lista:
                erros.append('É obrigatório ter o material Promo para essa categoria.')

        elif 'PRM404' == codigo:
            if 'Web Sites' not in lista and 'Digital' not in lista:
                erros.append(
                    'É obrigatório ter o um dos desses materiais Web Sites, Digital para essa categoria.')

        elif 'PRM4' in codigo:
            if 'Promo' not in lista:
                erros.append('É obrigatório ter o material Promo para essa categoria.')

        elif 'RAD1' in codigo or 'RAD20' in codigo:
            if 'Rádio' not in lista:
                erros.append('É obrigatório ter o material Rádio para essa categoria.')

        # Regra 16
        if 'TEC10' in codigo:
            if 'Filme' not in lista:
                erros.append('É obrigatório ter o material Filme para essa categoria.')

        elif 'TEC206' == codigo:
            if 'Rádio' not in lista and 'Filme' not in lista:
                erros.append('É obrigatório ter o material Rádio ou Filme para essa categoria.')

        elif 'TEC201' == codigo or 'TEC202' == codigo or 'TEC204' == codigo:
            if 'Rádio' not in lista:
                erros.append('É obrigatório ter o material Rádio para essa categoria.')

        elif 'TEC203' == codigo or 'TEC205' == codigo or 'TEC206' == codigo:
            if 'Filme' not in lista:
                erros.append('É obrigatório ter o material Filme para essa categoria.')

        elif 'TEC30' in codigo:
            if 'Jornal' not in lista and 'Revista' not in lista and 'Exterior' not in lista and 'Promo' not in lista:
                erros.append(
                    'É obrigatório ter um desses materiais: Jornal, Revista, Exterior ou Promo para essa categoria.')

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


    # return redirect('/admin/inscricao/inscricao/%s/change/#tabs-2' % inscricao)

def delete_material(request, pk):
    material = Material.objects.get(id=pk)
    material.delete()
    messages.success(request, 'Material apagado com sucesso.')
    return redirect(request.GET['to'])

def url_redirect(request):
    return redirect(request.GET['to'])