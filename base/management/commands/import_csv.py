#-*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.apps import apps
import csv

from base.models import Premiacao

headers = [
    {'filename': 'premiacoes.csv', 'app': 'base', 'modelo': 'Premiacao', 'fields': ['codigo','nome','ordem']},
    {'filename': 'formatos.csv', 'app': 'base', 'modelo': 'Formato', 'fields': ['codigo', 'nome', 'cod_premiacao']},
    {'filename': 'area.csv', 'app': 'base', 'modelo': 'Area', 'fields': ['codigo', 'descricao']},
    {'filename': 'categoria.csv', 'app': 'base', 'modelo': 'Categoria', 'fields': ['codigo', 'nome']},
    {'filename': 'atividade.csv', 'app': 'base', 'modelo': 'Atividade', 'fields': ['nome']},
]


def find_header(filename):
    for header in headers:
        if header['filename'] == filename:
            return header


class Command(BaseCommand):
    label = 'Importação CSV Batch'

    def add_arguments(self, parser):
        parser.add_argument('tabela', type=str, help='Nome da tabela em formato CSV')

    def handle(self, *args, **options):
        file_name = options['tabela']
        classe = find_header(file_name)
        if not classe:
            raise Exception('Classe %s não encontrada')
        modelo = apps.get_model(classe['app'], classe['modelo'])
        with open(file_name, encoding='iso-8859-1') as csv_file:
            reader = csv.reader(csv_file, delimiter=';', quotechar='"')
            reader.__next__()  # skip header
            header = classe['fields']
            for row in reader:
                _object_dict = {key: value for key, value in zip(header, row)}
                modelo.objects.create(**_object_dict)






