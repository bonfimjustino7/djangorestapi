from django.db import models


class Empresa(models.Model):
    nome = models.CharField(max_length=60)


class Inscricao(models.Model):
    nome = models.CharField(max_length=60)
