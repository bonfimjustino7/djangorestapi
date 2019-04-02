# coding:utf-8
from django import forms
#Isnard 10/06/2012 - #0001 - Inclusao da classe SpanWidget e comentario da UFChoiceFormField
from django.utils.safestring import mark_safe
from django.forms.utils import flatatt
from django.forms.widgets import HiddenInput

#Widget Button
"""
Usage:

ButtonField(label="", initial=u"Your submit button text")
"""

from django.utils import html

class ButtonWidget(forms.Widget):
    def render(self, name, value, attrs=None):
        return mark_safe(u'<button type="button" name="%s" id="id_%s">%s</button>' % (html.escape(name), html.escape(name), html.escape(value)))

class ButtonField(forms.Field):
    widget = ButtonWidget

    def prepare_value(self, value):
        return self.initial

    def to_python(self, value):
        return self.initial

    def clean(self, value):
        return self.initial

#Widget Button

class SpanWidget(forms.Widget):
    def render(self, name, value, attrs=None):
        if value is None:
            value = ''

        return mark_safe(u'<span%s>%s</span>\n%s' % (
            flatatt(self.build_attrs(attrs)),
            value,
            HiddenInput().render(name, value)
        ))


class BRDateFormField(forms.DateField):
    def __init__(self, *args, **kwargs):
        super(BRDateFormField, self).__init__(*args, **kwargs)
        self.widget.format = '%d/%m/%Y'
        # Aqui ele irá aceitar a data no formato brasileiro e no formato que o JS do calendário entrega para o campo
        self.input_formats = ['%d/%m/%Y','%Y-%m-%d']


class BRDecimalFormField(forms.DecimalField):
    def __init__(self, *args, **kwargs):
        super(BRDecimalFormField, self).__init__(*args, **kwargs)
        self.localize = True
        self.widget.input_type = 'text'
        self.widget.is_localized = True

class CustomUserChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
         return obj.get_full_name() or obj.username

class ImportGroupForm(forms.Form):
    json = forms.FileField(required=True)