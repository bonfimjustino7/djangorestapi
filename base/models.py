# coding: utf-8
from django.db import models
from django.contrib.auth.models import User


def ano_corrente():
    return 2019


class Regional(models.Model):
    codigo = models.CharField('Código', max_length=2)
    nome = models.CharField(max_length=30)
    estados = models.CharField(max_length=100, help_text='Separe os estados com vírgula', null=True)

    class Meta:
        ordering = ('nome', )
        verbose_name_plural = 'Regionais'

    def __str__(self):
        return self.nome


class UF(models.Model):
    sigla = models.CharField(max_length=2,primary_key=True)
    nome = models.CharField(max_length=40)

    class Meta:
        ordering = ('sigla', )
        verbose_name = u'UF'
        verbose_name_plural = u'Unidades da Federação'

    def __str__(self):
        return self.sigla


# Tipos de Materiais que serão julgados
class TipoMaterial(models.Model):
    descricao = models.CharField('Descrição', max_length=40)
    arquivo = models.BooleanField('Permite anexar arquivo', default=False)
    url = models.BooleanField('Permite URL', default=False)
    roteiro = models.BooleanField('Permite registro de roteiros', default=False)

    def __str__(self):
        return u'%s' % self.descricao

    class Meta:
        ordering = ('descricao', )
        verbose_name = u'Tipo de Material'
        verbose_name_plural = u'Tipos de Materiais'


class Premiacao(models.Model):
    nome = models.CharField(max_length=40)
    codigo = models.CharField(max_length=3)
    ordem = models.SmallIntegerField()
    materiais = models.ManyToManyField(TipoMaterial)

    def __str__(self):
        return self.nome

    class Meta:
        ordering = ('ordem', )
        verbose_name = 'Premiação'
        verbose_name_plural = 'Premiações'


class Formato(models.Model):
    nome = models.CharField(max_length=40)
    codigo = models.CharField(max_length=3)
    premiacao = models.ForeignKey(Premiacao, null=True, on_delete=models.PROTECT, verbose_name='Premiação')
    cod_premiacao = models.CharField(max_length=3) # Temporário - só para o import

    def __str__(self):
        return self.nome

    class Meta:
        ordering = ('nome', )


# Área de Atuação da empresa
class Area(models.Model):
    codigo = models.CharField(max_length=8)
    descricao = models.CharField(max_length=40)

    class Meta:
        ordering = ('descricao', )
        verbose_name = 'Área de Atividade'
        verbose_name_plural = 'Áreas de Atividade'

    def __str__(self):
        return self.descricao


# Categorias da Inscrição
class Categoria(models.Model):
    codigo = models.CharField('Código', max_length=6)
    nome = models.CharField(max_length=40)
    descricao = models.TextField('Texto explicativo')
    grupo = models.BooleanField(default=False)
    premiacao = models.ForeignKey(Premiacao)

    class Meta:
        ordering = ('codigo', )

    def __str__(self):
        return u'%s' % self.nome


PREMIO_STATUS = (
        ('A', 'Aberto para Inscrições'),
        ('F', 'Inscrições encerradas'),
        ('C', 'Concluído'),
    )


class Premio(models.Model):
    ano = models.SmallIntegerField()
    regional = models.ForeignKey(Regional, on_delete=models.PROTECT)
    status = models.CharField(max_length=1, choices=PREMIO_STATUS, default='A')

    def __str__(self):
        return '%s' % self.ano

    def descricao_completa(self):
        return '{}/{}'.format(
            self.regional,
            self.ano
        )

    class Meta:
        ordering = ('ano', )
        verbose_name = 'Premio'
        verbose_name_plural = 'Premios'
