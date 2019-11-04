from rest_framework.serializers import ModelSerializer
from pessoa.models import Pessoa
from django.contrib.auth.models import User

class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class PessoaSerializer(ModelSerializer):
    usuario = UserSerializer(many=False)
    class Meta:
        model = Pessoa
        fields = ['id', 'usuario', 'primeiro_nome', 'sobrenome', 'idade', 'cpf']