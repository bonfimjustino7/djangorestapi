#coding: utf-8
from django.db import models
from django.contrib.auth.models import User

class Regional(models.Model):
	nome = models.CharField(max_length = 30)

	class Meta:
		ordering = ('nome', )
		verbose_name_plural = 'Regionais'

	def __str__(self):
		return self.nome

class Categoria(models.Model):
	nome = models.CharField(max_length = 40)
	descricao = models.TextField()

	def __str__(self):
		return self.nome

class Premiacao(models.Model):
	nome = models.CharField(max_length = 40)
	codigo = models.CharField(max_length = 3)
	ordem = models.SmallIntegerField()

	def __str__(self):
		return self.nome

	class Meta:
		ordering = ('nome', )
		verbose_name = 'Premiação'
		verbose_name_plural = 'Premiações'

class Formato(models.Model):
	nome = models.CharField(max_length = 40)
	codigo = models.CharField(max_length = 3)
	premiacao = models.ForeignKey(Premiacao, null = True, on_delete = models.PROTECT)
	cod_premiacao = models.CharField(max_length = 3) # Temporário - só para o import

	def __str__(self):
		return self.nome

class Atividade(models.Model):
	nome = models.CharField(max_length = 40)

	def __str__(self):
		return self.nome

	class Meta:
		ordering = ('nome', )

PREMIO_STATUS = (
		('A', 'Aberto para Inscrições'),
		('F', 'Inscrições encerradas'),
		('C', 'Concluído'),
	)

class Premio(models.Model):
	ano = models.SmallIntegerField()
	premiacao = models.ForeignKey(Premiacao, on_delete = models.PROTECT)
	regional = models.ForeignKey(Regional, on_delete = models.PROTECT)
	status = models.CharField(max_length = 1, choices = PREMIO_STATUS)

	def __str__(self):
		return '{} {} ({})'.format(
			self.premiacao,
			self.regional,
			self.ano
		)

	class Meta:
		ordering = ('ano', )
		verbose_name = 'Premio'
		verbose_name_plural = 'Premios'

class Usuario(User):
	user = models.ForeignKey(User, null = True, blank = True, on_delete = models.CASCADE)
	token = models.CharField(max_length = 32)
