from django.contrib.auth.models import User
from django.db import models

class Pessoa(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    primeiro_nome = models.CharField('Primeiro Nome', max_length=50)
    sobrenome = models.CharField('Sobrenome', max_length=80)
    idade = models.IntegerField()
    cpf = models.CharField('CPF', max_length=11)

    def __str__(self):
        return self.primeiro_nome

class Endereco(models.Model):
    endereco = models.CharField('Endereço', max_length=50)
    numero = models.IntegerField()
    rua = models.CharField(max_length=50)
    bairro = models.CharField(max_length=50)

    def __str__(self):
        return self.endereco