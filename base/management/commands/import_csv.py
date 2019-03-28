#-*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.apps import apps
import csv

from tablib import Dataset
from import_export import resources

tabela = {'origem': 'premiacoes', 'destino': 'Premiacao'}

from base.models import Premiacao

headers = [
    {'filename': 'premiacoes.csv', 'app': 'base', 'modelo': 'Premiacao', 'fields': ['codigo','nome','ordem']},
    {'filename': 'formatos.csv', 'app': 'base', 'modelo': 'Formato', 'fields': ['codigo', 'nome', 'cod_premiacao']},
    {'filename': 'regionais.csv', 'app': 'base', 'modelo': 'Regional', 'fields': ['codigo', 'nome']},
    {'filename': 'area.csv', 'app': 'base', 'modelo': 'Area', 'fields': ['codigo', 'nome']},
    {'filename': 'categoria.csv', 'app': 'base', 'modelo': 'Categoria', 'fields': ['codigo', 'nome']},
    {'filename': 'atividade.csv', 'app': 'base', 'modelo': 'Atividade', 'fields': ['codigo', 'nome']},
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
        modelo = apps.get_model(classe['base'], classe['modelo'])
        with open(file_name, encoding='iso-8859-1') as csv_file:
            reader = csv.reader(csv_file, delimiter=';', quotechar='"')
            reader.__next__()  # skip header
            header = classe['header']
            for row in reader:
                _object_dict = {key: value for key, value in zip(header, row)}
                modelo.objects.create(**_object_dict)

    def handle2(self, *args, **options):
        filename = options['tabela']
        resource = resources.modelresource_factory(model=Premiacao)()
        arquivo = open(filename, encoding='iso-8859-1')
        dataset = Dataset()
        dataset.load(arquivo.read(), format='csv')
        result = resource.import_data(dataset, dry_run=True)
        if result.has_errors():
            print('error')
            for row in result.invalid_rows:
                print(row)
        else:
            for row in result.rows:
                print(row)

        #num_gravados = 0
        #for registro in csv.DictReader(arquivo):
        #    resource.import_row(registro)
        #   num_gravados += 1
        #print('Registros gravados: %d' % num_gravados)









