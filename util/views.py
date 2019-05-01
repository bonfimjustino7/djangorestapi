from util.stdlib import server_status
from util.models import EmailAgendado, Recurso
from django.http import HttpResponse
import json as simplejson


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