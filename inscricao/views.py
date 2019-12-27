from django.http import HttpResponse
from django.shortcuts import render
import json
from base.models import Premio, Premiacao


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
           # 'roteiro': reg[4]
        })
    return HttpResponse(json.dumps(result), content_type='application/json')