from django.http import HttpResponse
from django.shortcuts import render
import json
from base.models import Premio, Premiacao, Regional, TipoMaterial
from inscricao.models import Material


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
