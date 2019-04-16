# coding:utf-8
from django.db import models
from django.forms.fields import Field
from django.core.serializers.json import DjangoJSONEncoder

import ast, json, os, uuid

from .forms import BRDateFormField, BRDecimalFormField


def formata_nome_do_arquivo(objeto, nome_arquivo):
    nome, extensao = os.path.splitext(nome_arquivo)
    return os.path.join('imagens', str(uuid.uuid4()) + extensao.lower())


class BRDateField(models.DateField):
    def formfield(self, **kwargs):
        kwargs.update({'form_class': BRDateFormField})
        return super(BRDateField, self).formfield(**kwargs)


class BRDecimalField(models.DecimalField):
    def formfield(self, **kwargs):
        kwargs.update({'form_class': BRDecimalFormField})
        return super(BRDecimalField, self).formfield(**kwargs)


class JSONFormField(Field):
    def clean(self, value):

        if not value and not self.required:
            return None

        value = super(JSONFormField, self).clean(value)

        if isinstance(value, str):
            try:
                json.loads(value)
            except ValueError:
                pass # Error('Invalid JSON')
        return value


class JSONField(models.TextField):
    """JSONField is a generic textfield that serializes/unserializes JSON objects"""

    def __init__(self, *args, **kwargs):
        self.dump_kwargs = kwargs.pop('dump_kwargs', {'cls': DjangoJSONEncoder})
        self.load_kwargs = kwargs.pop('load_kwargs', {})

        super(JSONField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        """Convert string value to JSON"""
        if isinstance(value, str):
            try:
                return json.loads(value, **self.load_kwargs)
            except ValueError:
                pass
        return value

    def get_db_prep_value(self, value, connection, prepared=False):
        """Convert JSON object to a string"""

        if isinstance(value, str):
            return value
        return json.dumps(value, **self.dump_kwargs)

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_prep_value(value)

    def value_from_object(self, obj):
        return json.dumps(super(JSONField, self).value_from_object(obj))

    def formfield(self, **kwargs):

        if "form_class" not in kwargs:
            kwargs["form_class"] = JSONFormField

        field = super(JSONField, self).formfield(**kwargs)

        if not field.help_text:
            field.help_text = "Enter valid JSON"

        return field
