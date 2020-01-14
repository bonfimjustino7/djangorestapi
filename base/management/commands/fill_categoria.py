from django.core.management.base import BaseCommand
from django.apps import apps
import csv

from base.models import Categoria, Premiacao, Formato


class Command(BaseCommand):
    label = 'Atualização FK'

    def handle(self, *args, **options):
        for registro in Categoria.objects.all():
            codigo = registro.codigo[0:3]
            if not registro.premiacao:
                registro.premiacao = Premiacao.objects.get(codigo=codigo)
                registro.save()

        for registro in Formato.objects.all():
            registro.premiacao = Premiacao.objects.get(codigo=registro.cod_premiacao)
            registro.save()

