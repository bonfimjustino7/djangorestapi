from django.db import models
from localflavor.br.forms import BRCNPJField
from django.contrib.auth.models import User
from base.models import *


class Usuario(models.Model):
    nome_completo = models.CharField(max_length=80)
    user = models.ForeignKey(User, on_delete=models.PROTECT)

    class Meta:
        verbose_name = u'Usuário'
        verbose_name_plural = u'Usuários'


class Empresa(models.Model):
    nome = models.CharField(max_length=60)
    cnpj = BRCNPJField()
    area = models.ForeignKey(Area, on_delete=models.PROTECT)
    regional = models.ForeignKey(Regional, on_delete=models.PROTECT)
    cep = models.CharField(u'CEP', max_length=8, blank=True, null=True)
    uf = models.ForeignKey(UF, blank=True, null=True, on_delete=models.PROTECT)
    municipio = models.CharField(u'Município', max_length=150, blank=True, null=True)
    bairro = models.CharField(max_length=80, blank=True, null=True)
    endereco = models.CharField(u'Endereço', max_length=100, blank=True, null=True)
    ddd = models.CharField('DDD', max_length=2)
    telefone = models.CharField(u'Telefone', max_length=9, blank=True, null=True, help_text=u'XXXXX-XXXX')
    celular = models.CharField(u'Celular', max_length=9, blank=True, null=True, help_text=u'XXXXX-XXXX')
    homepage = models.URLField(u'Home Page da Empresa', blank=True, null=True)
    email = models.EmailField(u'E-Mail da Empresa', blank=True, null=True, help_text='Apenas se a empresa tiver um email central')
    VP_Nome = models.CharField('VP ou Diretor da Empresa', max_length=100)
    VP_Cargo = models.CharField('Cargo VP ou Diretor', max_length=60)
    VP_Email = models.EmailField(u'E-Mail', blank=True, null=True)
    VP_DDD = models.CharField('DDD', max_length=2)
    VP_Telefone = models.CharField(u'Celular', max_length=9, blank=True, null=True, help_text=u'XXXXX-XXXX')
    C1_Nome = models.CharField('VP ou Diretor da Empresa', max_length=100)
    C1_Cargo = models.CharField('Cargo VP ou Diretor', max_length=60)
    C1_Email = models.EmailField(u'E-Mail', blank=True, null=True)
    C1_DDD = models.CharField('DDD', max_length=2)
    C1_Telefone = models.CharField(u'Celular', max_length=9, blank=True, null=True, help_text=u'XXXXX-XXXX')
    C2_Nome = models.CharField('VP ou Diretor da Empresa', max_length=100)
    C2_Cargo = models.CharField('Cargo VP ou Diretor', max_length=60)
    C2_Email = models.EmailField(u'E-Mail', blank=True, null=True)
    C2_DDD = models.CharField('DDD', max_length=2)
    C2_Telefone = models.CharField(u'Celular', max_length=9, blank=True, null=True, help_text=u'XXXXX-XXXX')

    def __str__(self):
        return u'%s' % self.nome

class EmpresaAgencia(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    agencia = models.CharField(max_length=40)
    uf = models.ForeignKey(UF, on_delete=models.PROTECT)

    class Meta:
        verbose_name = u'Agência'
        verbose_name_plural = u'Agências'

    def __str__(self):
        return u'%s (%s)' % (self.agencia, self.uf)


class EmpresaUsuario(models.Model):
    empresa = models.ForeignKey(Empresa,on_delete=models.CASCADE)
    usuario = models.ForeignKey(Usuario,on_delete=models.CASCADE)
    dtinclusao = models.DateTimeField(auto_now_add=True)


class Inscricao(models.Model):
    premio = models.ForeignKey(Premio,on_delete=models.PROTECT)
    usuario = models.ForeignKey(Usuario,on_delete=models.PROTECT)
    empresa = models.ForeignKey(Empresa,on_delete=models.PROTECT)
    seq = models.IntegerField('Seq')
    formato = models.ForeignKey(Formato,on_delete=models.PROTECT)
    titulo = models.CharField(max_length=60)
    agencia = models.ForeignKey(EmpresaAgencia,on_delete=models.PROTECT)
    categoria = models.ForeignKey(Categoria,on_delete=models.PROTECT)
    parcerias = models.CharField(max_length=50, null=True, blank=True)
    cliente = models.CharField(max_length=60, null=True, blank=True)
    produto = models.CharField(max_length=30, null=True, blank=True)
    dtinicio = models.DateField('Veiculação ou Início')
    isolada = models.BooleanField(default=False)
    DiretorCriacao = models.CharField(max_length=100, null=True, blank=True)
    Planejamento = models.CharField(max_length=100, null=True, blank=True)
    Redacao = models.CharField(max_length=140, null=True, blank=True)
    DiretorArte = models.CharField(max_length=140, null=True, blank=True)
    ProducaoGrafica = models.CharField(max_length=80, null=True, blank=True)
    ProducaoRTVC = models.CharField(max_length=80, null=True, blank=True)
    TecnologiaDigital = models.CharField(max_length=80, null=True, blank=True)
    OutrosAgencia1 = models.CharField(max_length=80, null=True, blank=True)
    OutrosAgencia2 = models.CharField(max_length=80, null=True, blank=True)
    Midia = models.CharField(max_length=60, null=True, blank=True)
    Atendimento = models.CharField(max_length=80, null=True, blank=True)
    Aprovacao = models.CharField(max_length=100, null=True, blank=True)
    ProdutoraFilme = models.CharField(max_length=50, null=True, blank=True)
    DiretorFilme = models.CharField(max_length=50, null=True, blank=True)
    ProdutoraAudio = models.CharField(max_length=50, null=True, blank=True)
    DiretorAudio = models.CharField(max_length=50, null=True, blank=True)
    EstudioFotografia = models.CharField(max_length=40, null=True, blank=True)
    Fotografo = models.CharField(max_length=50, null=True, blank=True)
    EstudioIlustracao = models.CharField(max_length=40, null=True, blank=True)
    Ilustrador = models.CharField(max_length=50, null=True, blank=True)
    ManipulacaoDigital = models.CharField(max_length=40, null=True, blank=True)
    Finalizacao = models.CharField(max_length=40, null=True, blank=True)
    OutrosFornecedor1 = models.CharField(max_length=80, null=True, blank=True)
    OutrosFornecedor2 = models.CharField(max_length=80, null=True, blank=True)
    roteiro = models.TextField('Roteiro de Rádio', null=True, blank=True)

    def __str__(self):
        return u'%s' % (self.seq)

    class Meta:
        ordering = ('seq', )
        verbose_name = u'Inscrição'
        verbose_name_plural = u'Inscrições'
        indexes = [models.Index(fields=['usuario', 'empresa', 'seq']),]


class TipoMaterial(models.Model):
    descricao = models.CharField(max_length=40)

    def __str__(self):
        return u'%s' % (self.descricao)


class Material(models.Model):
    inscricao = models.ForeignKey(Inscricao, on_delete=models.CASCADE)
    tipo = models.ForeignKey(TipoMaterial, on_delete=models.PROTECT)
    arquivo = models.FileField(null=True, blank=True)
    url = models.URLField(null=True, blank=True)
    idsoundcloud = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return u'%s (%s)' % (self.formato, self.id)
