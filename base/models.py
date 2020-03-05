# coding: utf-8
from django.db import models
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from smart_selects.db_fields import ChainedForeignKey

def ano_corrente():
    import datetime
    now = datetime.datetime.now()
    return str(now.year)


class Regional(models.Model):
    codigo = models.CharField('Código', max_length=2)
    nome = models.CharField(max_length=30)
    estados = models.CharField(max_length=100, help_text='Separe os estados com vírgula', null=True)

    class Meta:
        ordering = ('nome', )
        verbose_name_plural = 'Regionais'

    # TODO: Na hora de salvar, verificar se não existe um estado em mais de uma regional
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
    youtube = models.BooleanField('Youtube/Vimeo obrigatórios', default=False)
    dicas = models.TextField('Dicas para preenchimento', blank=True, null=True)

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
    URLApoio = models.URLField('URL Apoio', blank=True, null=True)

    def __str__(self):
        return self.nome

    def url_nova_aba(self):
        return mark_safe('%s"target="_blank"' % self.URLApoio if self.URLApoio else '')

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
    nome = models.CharField(max_length=100)
    descricao = models.TextField('Texto explicativo')
    premiacao = models.ForeignKey(Premiacao, verbose_name='Premiação')

    class Meta:
        ordering = ('codigo', )

    def __str__(self):
        return u'%s' % self.nome


class Preco(models.Model):
    premiacao = models.ForeignKey(Premiacao, verbose_name='Premiação')
    categoria = ChainedForeignKey(Categoria, chained_field='premiacao', chained_model_field='premiacao',
                                  blank=True, null=True, help_text='Deixe em branco para o caso geral',
                                  show_all=False, on_delete=models.PROTECT)
    preco = models.DecimalField('Preço Regular', max_digits=16, decimal_places=2)
    preco_serie = models.DecimalField('Preço para Série', blank=True, null=True, max_digits=16, decimal_places=2)

    class Meta:
        ordering = ('premiacao', 'categoria', )
        verbose_name = 'Preço'

    def __str__(self):
        if self.categoria:
            return u'%s - %s' % (self.premiacao, self.categoria)
        else:
            return u'%s' % self.premiacao


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

    def total_inscricoes(self):
        return self.inscricao_set.count()
    total_inscricoes.short_description = 'Total de Inscrições'

    def total_inscricoes_pendentes(self):
        count = self.inscricao_set.filter(status='A').count()
        if count > 0:
            return mark_safe('<font color="red">%d</font>' % count)
        else:
            return '0'
    total_inscricoes_pendentes.short_description = 'Inscrições Pendentes'

    class Meta:
        ordering = ('ano', )
        verbose_name = 'Premio'
        verbose_name_plural = 'Premios'
