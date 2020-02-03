import os
from unicodedata import normalize

from inscricao.models import Material
from util.stdlib import server_status
from util.models import EmailAgendado, Recurso
from django.http import HttpResponse
import json as simplejson

def tokenize(text):
    new_text = normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII')
    return new_text.replace(' ', '-')

def status(request):
    json = server_status()
    status_email = 0  # Enabled
    if EmailAgendado.objects.latest('pk').status == 'E':
        status_email = 1  # Com erro
    elif not Recurso.objects.get_or_create(recurso='EMAIL')[0].ativo:
        status_email = 2  # Disable
    json['mail'] = {
        'Available': status_email
    }
    return HttpResponse(simplejson.dumps(json), content_type="application/json")

def montar_nome(request, id):

    material = Material.objects.get(id=id)
    inscricao = material.inscricao
    extencao = material.arquivo.name.split('/')[1]
    filename = str(inscricao.agencia).upper() + '-' + str((inscricao.titulo).lower()) + '(%s)' % str(material.tipo)[:3] + '-'+ extencao
    response = HttpResponse(material.arquivo, content_type="application/file")
    response['Content-Disposition'] = 'attachment; filename=%s' % (tokenize(filename))
    return response