from django.contrib.auth.models import User
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.response import Response

from pessoa.models import Pessoa
from pessoa.api.serializer import PessoaSerializer, UserSerializer


class PessoaViewSet(viewsets.ModelViewSet):
    queryset = Pessoa.objects.all()
    serializer_class = PessoaSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    ordering_fields = ['primeiro_nome', 'sobrenome', 'idade']
    ordering = ['primeiro_nome']
    search_fields = ['primeiro_nome', 'sobrenome', 'idade']
    permission_classes = (IsAuthenticated, DjangoModelPermissions) #deixa o viewset sendo obrigatorio a autenticacao

    def get_queryset(self):
        queryset = self.queryset
        usuario = self.request.query_params.get('usuario', None)
        idade = self.request.query_params.get('idade', None)

        if usuario:
            queryset = Pessoa.objects.filter(usuario__first_name__iexact=usuario)

        if idade:
            queryset = queryset.filter(idade=idade)

        return queryset


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()

    # Primeiro metodo a ser executado quando for chamado o GET
    # def list(self, request, *args, **kwargs):
    #     return Response({'teste': 123})

    # def create(self, request, *args, **kwargs):
    #     return Response({'Hello': request.data['first_name']})

    # def destroy(self, request, *args, **kwargs):
    #     pass

    # É acionando quando se faz um GET com id (argumento)
    # def retrieve(self, request, *args, **kwargs):
    #     pass

    # #Acionado quando se faz um PUT
    # def update(self, request, *args, **kwargs):
    #     pass

    # #Acionando quando se faz um PATCH
    # def partial_update(self, request, *args, **kwargs):
    #     pass
