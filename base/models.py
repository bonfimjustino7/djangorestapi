from django.db import models


class Regional(models.Model):
    nome = models.CharField(max_length=30)

    class Meta:
        ordering = ('nome', )
        verbose_name_plural = 'Regionais'

    def __str__(self):
        return u'%s' % self.nome


class UF(models.Model):
    sigla = models.CharField(max_length=2,primary_key=True)
    nome = models.CharField(max_length=40)


class Categoria(models.Model):
    codigo = models.CharField(max_length=6)
    nome = models.CharField(max_length=40)
    descricao = models.TextField()
    grupo = models.BooleanField(default=False)

    def __str__(self):
        return u'%s' % self.nome


class Area(models.Model):
    codigo = models.CharField(max_length=8)
    descricao = models.CharField(max_length=40)

    def __str__(self):
        return u'%s' % self.nome


class Premiacao(models.Model):
    nome = models.CharField(max_length=40)
    codigo = models.CharField(max_length=3)
    ordem = models.SmallIntegerField()

    def __str__(self):
        return u'%s' % self.nome

    class Meta:
        ordering = ('nome', )
        verbose_name = 'Premiação'
        verbose_name_plural = 'Premiações'


class Formato(models.Model):
    nome = models.CharField(max_length=40)
    codigo = models.CharField(max_length=3)
    premiacao = models.ForeignKey(Premiacao, null=True, on_delete=models.PROTECT)
    cod_premiacao = models.CharField(max_length=3) # Temporário - só para o import

    def __str__(self):
        return u'%s' % self.nome


class Atividade(models.Model):
    nome = models.CharField(max_length=40)

    def __str__(self):
        return u'%s' % self.nome

    class Meta:
        ordering = ('nome', )


PREMIO_STATUS = (
        ('A', u'Aberto para Inscrições'),
        ('F', u'Inscrições encerradas'),
        ('C', u'Concluído'),
    )


class Premio(models.Model):
    ano = models.SmallIntegerField()
    premiacao = models.ForeignKey(Premiacao, on_delete=models.PROTECT)
    regional = models.ForeignKey(Regional, on_delete=models.PROTECT)
    status = models.CharField(max_length=1, choices=PREMIO_STATUS)

    def __str__(self):
        return u'%s %s (%d)' % (self.premiacao,self.regional,self.ano)

    class Meta:
        ordering = ('ano', )
        verbose_name = u'Premio'
        verbose_name_plural = u'Premios'
