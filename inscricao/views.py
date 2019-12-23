from django.http import HttpResponse
from django.shortcuts import render
import json
from base.models import Premio, Premiacao


def tipo_materiais(request, id):
    premiacao = Premiacao.objects.get(id=id)
    context = premiacao.materiais.all().values_list('id', 'descricao').order_by('id')
    result = []
    for reg in context:
        result.append({
            'id': reg[0],
            'text': reg[1],
        })
    return HttpResponse(json.dumps(result), content_type='application/json')