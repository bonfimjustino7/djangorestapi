import os
import uuid

from django.db import models
from django.dispatch import receiver
from localflavor.br.forms import BRCNPJField
from django.contrib.auth.models import User
from base.models import *
from colunistas import settings
from util.stdlib import upper_first
from smart_selects.db_fields import ChainedForeignKey, ChainedManyToManyField
from django.db.models.signals import m2m_changed, post_save, post_delete


STATUS_ENVIO = (('A', 'Em aberto'), ('F', 'Finalizado'))


class FileField(models.FileField):
    def save_form_data(self, instance, data):
        if data is not None:
            file = getattr(instance, self.attname)
            if file != data:
                file.delete(save=False)
        super(FileField, self).save_form_data(instance, data)


class Usuario(models.Model):
    nome_completo = models.CharField('Nome', max_length=80)
    user = models.ForeignKey(User, on_delete=models.PROTECT)

    class Meta:
        verbose_name = u'Usuário'
        verbose_name_plural = u'Usuários'

    def __str__(self):
        return u'%s (%s)' % (self.nome_completo, self.user)


class Empresa(models.Model):
    nome = models.CharField('Nome da Empresa',max_length=60)
    cnpj = BRCNPJField()
    area = models.ForeignKey(Area, verbose_name = 'Área', on_delete=models.PROTECT)
    regional = models.ForeignKey(Regional, on_delete=models.PROTECT)
    cep = models.CharField(u'CEP', max_length=8, blank=True, null=True)
    uf = models.ForeignKey(UF, blank=True, null=True, on_delete=models.PROTECT)
    cidade = models.CharField(u'Cidade', max_length=23, blank=True, null=True)
    bairro = models.CharField(max_length=20, blank=True, null=True)
    endereco = models.CharField(u'Endereço', max_length=100, blank=True, null=True)
    ddd = models.CharField('DDD', max_length=2)
    telefone = models.CharField(u'Telefone', max_length=10, blank=True, null=True, help_text=u'XXXXX-XXXX')
    celular = models.CharField(u'Celular', max_length=10, blank=True, null=True, help_text=u'XXXXX-XXXX')
    homepage = models.URLField(u'Home Page da Empresa', blank=True, null=True)
    email = models.EmailField(u'E-Mail da Empresa', blank=True, null=True,
                              help_text='Apenas se a empresa tiver um email central')
    VP_Nome = models.CharField('VP ou Diretor da Empresa', max_length=100)
    VP_Cargo = models.CharField('Cargo VP ou Diretor', max_length=60)
    VP_Email = models.EmailField(u'E-Mail', blank=True, null=True)
    VP_DDD = models.CharField('DDD', max_length=2)
    VP_Telefone = models.CharField(u'Celular', max_length=9, blank=True, null=True, help_text=u'XXXXX-XXXX')
    C1_Nome = models.CharField('VP ou Diretor da Empresa', max_length=100, null = True, blank = True)
    C1_Cargo = models.CharField('Cargo VP ou Diretor', max_length=60, null = True, blank = True)
    C1_Email = models.EmailField(u'E-Mail', blank=True, null=True)
    C1_DDD = models.CharField('DDD', max_length=2, null = True, blank = True)
    C1_Telefone = models.CharField(u'Celular', max_length=9, blank=True, null=True, help_text=u'XXXXX-XXXX')
    C2_Nome = models.CharField('VP ou Diretor da Empresa', max_length=100, null = True, blank = True)
    C2_Cargo = models.CharField('Cargo VP ou Diretor', max_length=60, null = True, blank = True)
    C2_Email = models.EmailField(u'E-Mail', blank=True, null=True)
    C2_DDD = models.CharField('DDD', max_length=2, null=True, blank=True)
    C2_Telefone = models.CharField(u'Celular', max_length=9, blank=True, null=True, help_text=u'XXXXX-XXXX')
    status = models.CharField('Situação', max_length=1, choices=STATUS_ENVIO, default='A')

    def __str__(self):
        return u'%s' % self.nome

    def save(self, request=False, *args, **kwargs):
        self.nome = self.nome.upper()
        self.cep = self.cep.replace('-', '')
        self.VP_Nome = upper_first(self.VP_Nome)
        self.VP_Cargo = upper_first(self.VP_Cargo)
        self.C1_Nome = upper_first(self.C1_Nome)
        self.C1_Cargo = upper_first(self.C1_Cargo)
        self.C2_Nome = upper_first(self.C2_Nome)
        self.C2_Cargo = upper_first(self.C2_Cargo)
        self.bairro = upper_first(self.bairro)
        self.endereco = upper_first(self.endereco)
        super(Empresa, self).save(*args, **kwargs)


class EmpresaAgencia(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    agencia = models.CharField('Nome da Agência', max_length=40)
    uf = models.ForeignKey(UF, on_delete=models.PROTECT)

    class Meta:
        verbose_name = u'Agência'
        verbose_name_plural = u'Agências'

    def __str__(self):
        return u'%s (%s)' % (self.agencia, self.uf)


class EmpresaUsuario(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    dtinclusao = models.DateTimeField(auto_now_add=True)


texto_outros_autores = 'Utilize o formato: "Função, Fulano, Beltrano e Sicrano'
texto_outros_creditos = 'Outros Créditos de Fornecedores'

STATUS_INSCRICAO = (
    ('A', 'Em edição'),
    ('V', 'Validada'),
)


class Inscricao(models.Model):
    premiacao = models.ForeignKey(Premiacao, on_delete=models.PROTECT, verbose_name='Premiação')
    premio = models.ForeignKey(Premio, on_delete=models.PROTECT, null=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.PROTECT)
    empresa = models.ForeignKey(Empresa, on_delete=models.PROTECT)
    seq = models.IntegerField('Seq')
    titulo = models.CharField('Título', max_length=60)
    agencia = ChainedForeignKey(EmpresaAgencia, chained_field='empresa', chained_model_field='empresa',
                                show_all=False, verbose_name='Agência')
    categoria = ChainedForeignKey(Categoria, chained_field='premiacao', chained_model_field='premiacao',
                                show_all=False, on_delete=models.PROTECT)
    cliente = models.CharField(max_length=60, null=True, blank=True)
    parcerias = models.CharField(max_length=50, null=True, blank=True)
    produto = models.CharField(max_length=30, null=True, blank=True)
    dtinicio = models.DateField('Veiculação ou Início')
    isolada = models.BooleanField(default=False)
    DiretorCriacao = models.CharField('Diretor de Criação', max_length=100,
                                      help_text=texto_outros_autores, null=True, blank=True)
    Planejamento = models.CharField('Planejamento', max_length=80, null=True, blank=True)
    Redacao = models.CharField('Redação', max_length=140, null=True, blank=True)
    DiretorArte = models.CharField('Diretor de Arte', max_length=140, null=True, blank=True)
    ProducaoGrafica = models.CharField('Produção Gráfica', max_length=80, null=True, blank=True)
    ProducaoRTVC = models.CharField('Produção RTVC', max_length=80, null=True, blank=True)
    TecnologiaDigital = models.CharField('Tecnologia Digital', max_length=80, null=True, blank=True)
    OutrosAgencia1 = models.CharField('Outros Créditos', max_length=80,
                                      null=True, blank=True, help_text=texto_outros_autores)
    OutrosAgencia2 = models.CharField('Outros Créditos', max_length=80,
                                      null=True, blank=True, help_text=texto_outros_autores)
    OutrosAgencia3 = models.CharField('Outros Créditos', max_length=80,
                                      null=True, blank=True, help_text=texto_outros_autores)
    OutrosAgencia4 = models.CharField('Outros Créditos', max_length=80,
                                      null=True, blank=True, help_text=texto_outros_autores)
    Midia = models.CharField('Mídia', max_length=80, null=True, blank=True)
    Atendimento = models.CharField('Atendimento', max_length=100, null=True, blank=True)
    Aprovacao = models.CharField('Aprovação', max_length=100, null=True, blank=True)
    ProdutoraFilme = models.CharField('Produtora do Filme', max_length=50, null=True, blank=True)
    DiretorFilme = models.CharField('Diretor do Filme', max_length=50, null=True, blank=True)
    ProdutoraAudio = models.CharField('Produtora de Áudio', max_length=50, null=True, blank=True)
    DiretorAudio = models.CharField('Diretor de Áudio', max_length=50, null=True, blank=True)
    EstudioFotografia = models.CharField('Estúdio de Fotografia', max_length=40, null=True, blank=True)
    Fotografo = models.CharField('Fotógrafo', max_length=50, null=True, blank=True)
    EstudioIlustracao = models.CharField('Estúdio de Ilustração', max_length=40, null=True, blank=True)
    Ilustrador = models.CharField(max_length=50, null=True, blank=True)
    ManipulacaoDigital = models.CharField('Manipulação Digital', max_length=40, null=True, blank=True)
    Finalizacao = models.CharField('Finalização', max_length=40, null=True, blank=True)
    OutrosFornecedor1 = models.CharField(texto_outros_creditos, max_length=80,
                                         help_text=texto_outros_autores, null=True, blank=True)
    OutrosFornecedor2 = models.CharField(texto_outros_creditos, max_length=80,
                                         help_text=texto_outros_autores, null=True, blank=True)
    OutrosFornecedor3 = models.CharField(texto_outros_creditos, max_length=80,
                                         help_text=texto_outros_autores, null=True, blank=True)
    OutrosFornecedor4 = models.CharField(texto_outros_creditos, max_length=80,
                                         help_text=texto_outros_autores, null=True, blank=True)
    dtinclusao = models.DateTimeField('Dt.Inclusão', auto_now_add=True, null=True, blank=True)
    dtexportacao = models.DateField('Dt.Exportação', null=True, blank=True)
    status = models.CharField(max_length=1, default='A', choices=STATUS_INSCRICAO)
    videocase = models.URLField('Videocase', max_length=512, null=True, blank=True)
    apresentacao = models.URLField('Apresentação', max_length=512, null=True, blank=True)

    def __str__(self):
        return u'%s' % self.seq

    class Meta:
        ordering = ('seq', )
        verbose_name = u'Inscrição'
        verbose_name_plural = u'Inscrições'
        indexes = [models.Index(fields=['usuario', 'empresa', 'seq']),]

    @property
    def resumo(self):
        return 'Jornais (3), Revistas (4), etc'

    def save(self, *args, **kwargs):
        if not self.seq:
            ultima = Inscricao.objects.filter(empresa=self.empresa).last()
            if ultima:
                seq_ant = ultima.seq
            else:
                seq_ant = 0
            self.seq = seq_ant + 1
        super(Inscricao, self).save(*args, **kwargs)


def path(self, filename):
    extension = os.path.splitext(filename)[-1]
    if self.id:
        filename = '%s' % self.id
    else:
        last_material = Material.objects.values('id').last()
        filename = '%s' % str(last_material['id']+1)

    new_filename = '%s/%s%s' % ('uploads', filename, extension)
    return new_filename


class Material(models.Model):
    inscricao = models.ForeignKey(Inscricao, on_delete=models.CASCADE)
    tipo = models.ForeignKey(TipoMaterial, on_delete=models.PROTECT)
    arquivo = FileField(upload_to=path, max_length=512, null=True, blank=True)
    url = models.URLField(null=True, blank=True)
    idsoundcloud = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return u'%s (%s)' % (self.tipo, self.id)

    class Meta:
        verbose_name = u'Material'
        verbose_name_plural = u'Materiais'
        ordering = ('tipo', 'id',)


@receiver(post_delete, sender=Material)
def handler_file(sender, **kwargs):
    filename = kwargs['instance'].arquivo
    if filename:
        path = os.path.join(settings.MEDIA_ROOT, filename.name)
        if os.path.exists(path):
            os.remove(path)
