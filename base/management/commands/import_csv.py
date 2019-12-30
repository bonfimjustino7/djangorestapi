from django.core.management.base import BaseCommand
from django.apps import apps
import csv

headers = [
    {'filename': 'premiacoes.csv', 'app': 'base', 'modelo': 'Premiacao', 'fields': ['codigo','nome','ordem']},
    {'filename': 'regional.csv', 'app': 'base', 'modelo': 'Regional', 'fields': ['codigo', 'nome',]},
    {'filename': 'formatos.csv', 'app': 'base', 'modelo': 'Formato', 'fields': ['codigo', 'nome', 'cod_premiacao']},
    {'filename': 'area.csv', 'app': 'base', 'modelo': 'Area', 'fields': ['codigo', 'descricao']},
    {'filename': 'uf.csv', 'app': 'base', 'modelo': 'UF', 'fields': ['nome', 'sigla']},
    {'filename': 'materiais.csv', 'app': 'base', 'modelo': 'TipoMaterial', 'fields': ['descricao', ]},
    {'filename': 'categoria.csv', 'app': 'base', 'modelo': 'Categoria', 'fields': ['codigo', 'nome', 'premiacao_id']},
]

from base.models import Categoria, Premiacao


def find_header(filename):
    for header in headers:
        if header['filename'] == filename:
            return header


class Command(BaseCommand):
    label = 'Importação CSV Batch'

    def add_arguments(self, parser):
        parser.add_argument('tabela', type=str, help='Nome da tabela em formato CSV')

    @staticmethod
    def import_categoria(filename):
        print('Import Categorias')
        with open('data/'+filename, mode='r', encoding='iso-8859-1') as csv_file:
            reader = csv.DictReader(csv_file, delimiter=';', quotechar='"')
            line_count = 0
            for row in reader:
                line_count += 1
                codigo = row['CodCategoria'][:3]
                try:
                    premiacao = Premiacao.objects.get(codigo=codigo)
                except Premiacao.DoesNotExist:
                    print('Premiação não encontrada %s' % codigo)
                    return
                if len(row['Categoria']) > 60:
                    print('Erro len: %s' % row['Categoria'])
                grupo = row['NomeDeGrupo'][0] == 'V'
                Categoria.objects.create(codigo=row['CodCategoria'], nome=row['Categoria'],
                                         descricao=row['Descricao'],
                                         premiacao=premiacao, grupo=grupo)
            print('Linhas: %d' % line_count)

    def handle(self, *args, **options):
        file_name = options['tabela']
        if file_name.find('categorias') >= 0:
            self.import_categoria(file_name)
            return

        classe = find_header(file_name)
        if not classe:
            raise Exception('Classe %s não encontrada' % file_name)
        modelo = apps.get_model(classe['app'], classe['modelo'])
        tot_reg = 0
        with open('data/'+file_name, encoding='iso-8859-1') as csv_file:
            reader = csv.reader(csv_file, delimiter=';', quotechar='"')
            reader.__next__()  # skip header
            header = classe['fields']
            for row in reader:
                _object_dict = {key: value for key, value in zip(header, row)}
                modelo.objects.create(**_object_dict)
                tot_reg += 1
        print('Registros importados: %d' % tot_reg)
