# coding:utf-8
#import datetime
import os
from itertools import chain

from django.db.models import ManyToManyField, ForeignKey
from django.forms import model_to_dict
from django.utils.text import capfirst


def only_numbers(value):
    # Retorna uma nova string, removendo qualquer caracter que não seja um número
    return ''.join(val for val in value if val.isdigit())


def nvl(objeto,alternativa):
    # simula a função clássica do Oracle: Retorna uma alternativa caso o objeto esteja vazio
    if objeto:
        return objeto
    else:
        return alternativa


def upper_first(value):
    # Retorna a string capitalizada, considerando preposições em Português
    result = ''
    if value:
        for sentence in value.lower().split(" "):
            if sentence in ['de', 'da', 'do', 'para', 'e', 'entre']:
                result = result + " " + sentence
            else:
                result = result + " " + capfirst(sentence)
    return result.lstrip()


# Retorna o objeto referenciado no PATH do request
def get_object_from_path(request, model):
    object_id = request.META['PATH_INFO'].strip('/').split('/')[-2]
    if object_id.isdigit():
        return model.objects.get(pk=object_id)
    raise model.DoesNotExist()


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def server_status():
    json = {}
    # HD
    devices_data = os.popen('df').read().split('\n')
    header = devices_data[0].split()
    for device in devices_data[1:]:
        if device:
            data = [int(data) if data.isdigit() else data for data in device.split()[1:]]
            json[device.split()[0]] = dict(zip(header[1:], data))
    # Memory
    memory_data = os.popen('free').read().split('\n')
    header = memory_data[0].split()
    for memory in memory_data[1:]:
        if memory:
            data = [int(data) if data.isdigit() else data for data in memory.split()[1:]]
            json[memory.split()[0]] = dict(zip(header, data))
    return json


def model_to_dict_verbose(instance, fields=None, exclude=None):
    """
    Returns a dict containing the data in ``instance`` suitable for passing as
    a Form's ``initial`` keyword argument. Keys in dict are exchanged for
    verbose names contained in the model.
    ``fields`` is an optional list of field names. If provided, only the named
    fields will be included in the returned dict.
    ``exclude`` is an optional list of field names. If provided, the named
    fields will be excluded from the returned dict, even if they are listed in
    the ``fields`` argument.
    """
    opts = instance._meta
    data = {}
    for f in chain(opts.concrete_fields, opts.virtual_fields, opts.many_to_many):
        if not getattr(f, 'editable', False):
            continue
        if fields and f.name not in fields:
            continue
        if exclude and f.name in exclude:
            continue
        verbose_name = opts.get_field(f.name).verbose_name
        if isinstance(f, ManyToManyField):
            # If the object doesn't have a primary key yet, just use an empty
            # list for its m2m fields. Calling f.value_from_object will raise
            # an exception.
            if instance.pk is None:
                data[verbose_name] = []
            else:
                # MultipleChoiceWidget needs a list of pks, not object instances.
                qs = f.value_from_object(instance)
                if qs._result_cache is not None:
                    data[verbose_name] = [item.pk for item in qs]
                else:
                    data[verbose_name] = list(qs.values_list('pk', flat=True))
        #TODO falta fazer com que o obj retorne a descricao do model em vez da id
        else:
            data[verbose_name] = f.value_from_object(instance)
    return data


def get_model_values_labels(obj, fields=None):
    '''
    :param obj: instancia do model.
    :param fields:  tupla ou lista de campos a serem retornados pela a função.
    :return: lista de labels e de values.
    '''
    values = []
    if fields is None:
        for field in get_model_labels(obj, fields):
            values.append(obj._meta.model.objects.values_list(field,  flat=True).get(id=obj.id))
    else:
        for field in fields:
            values.append(obj._meta.model.objects.values_list(field, flat=True).get(id=obj.id))

    labels = get_model_labels(obj, fields=fields)

    return [labels] + [values]

def get_model_labels(obj, fields=None):
    '''

    :param obj: instancia do model.
    :param fields: tupla ou lista de campos a serem retornados pela a função.
    :return: lista de labels.
    '''

    lista = []
    labels = {}
    if fields is None:
        labels = model_to_dict(obj)
    else:
        for field in fields:
            labels[field] = obj._meta.model.objects.values_list(field, flat=True).get(id=obj.id)

    for key, item in labels.items():
        lista.append(str(key))
    return lista
'''
def encode_utf8(text):
    m = magic.Magic(mime_encoding=True)
    encoding = m.from_buffer(text)
    try:
        text = text.decode(encoding).encode('utf-8')
    except:
        text = text.decode('iso-8859-1').encode('utf-8')
    return text
'''