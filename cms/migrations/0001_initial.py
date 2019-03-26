# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-09-16 11:07
from __future__ import unicode_literals

import cms.fields
import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import mptt.fields
import smart_selects.db_fields
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0008_alter_user_username_max_length'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=250, verbose_name='T\xedtulo')),
                ('slug', models.SlugField(blank=True, max_length=250, unique=True, verbose_name='slug')),
                ('header', models.TextField(blank=True, default=None, null=True, verbose_name='Chamada')),
                ('content', models.TextField(blank=True, default=None, null=True, verbose_name='Conte\xfado')),
                ('keywords', models.TextField(blank=True, default=None, null=True, verbose_name='Palavras Chaves')),
                ('created_at', models.DateField(default=django.utils.timezone.now, verbose_name='Dt.Cria\xe7\xe3o')),
                ('updated_at', models.DateField(auto_now=True, verbose_name='Dt.Altera\xe7\xe3o')),
                ('is_active', models.BooleanField(default=True, verbose_name='Est\xe1 ativo?')),
                ('allow_comments', models.CharField(choices=[(b'A', 'Permite coment\xe1rios'), (b'P', 'Permite coment\xe1rios privados'), (b'F', 'Fechado para novos coment\xe1rios'), (b'N', 'Sem coment\xe1rios')], default=b'N', max_length=1, verbose_name='Coment\xe1rios')),
                ('views', models.IntegerField(default=0, verbose_name='Visualiza\xe7\xf5es')),
                ('conversions', models.IntegerField(default=0, verbose_name='Convers\xf5es')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Autor')),
            ],
            options={
                'ordering': ['-created_at'],
                'verbose_name': 'Artigo',
            },
        ),
        migrations.CreateModel(
            name='ArticleArchive',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('header', models.TextField(blank=True, null=True, verbose_name='Chamada')),
                ('content', models.TextField(blank=True, null=True, verbose_name='Conte\xfado')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Dt.Altera\xe7\xe3o')),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cms.Article', verbose_name='Artigo')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Autor')),
            ],
            options={
                'ordering': ('updated_at',),
                'verbose_name': 'Vers\xe3o do Artigo',
                'verbose_name_plural': 'Vers\xf5es dos Artigos',
            },
        ),
        migrations.CreateModel(
            name='ArticleAttribute',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attrib', models.CharField(max_length=30, verbose_name='Atributo')),
                ('value', models.CharField(max_length=100, verbose_name='Valor')),
                ('active', models.BooleanField(default=False, verbose_name='Ativo')),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cms.Article', verbose_name='Artigo')),
            ],
            options={
                'verbose_name': 'Atributo do Artigo',
                'verbose_name_plural': 'Atributos do Artigo',
            },
        ),
        migrations.CreateModel(
            name='ArticleComment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateField(auto_now_add=True, verbose_name='Dt.Cria\xe7\xe3o')),
                ('author', models.CharField(max_length=60, verbose_name='Autor')),
                ('comment', models.TextField(verbose_name='Coment\xe1rio')),
                ('active', models.BooleanField(default=False, verbose_name='Ativo')),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cms.Article', verbose_name='Artigo')),
            ],
            options={
                'ordering': ('created_at',),
                'verbose_name': 'Coment\xe1rio',
                'verbose_name_plural': 'Coment\xe1rios',
            },
        ),
        migrations.CreateModel(
            name='EmailAgendado',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(default=b'', max_length=90)),
                ('status', models.CharField(choices=[(b'A', 'Aguardando envio manual...'), (b'S', 'Enviando...'), (b'R', 'Re-enviando'), (b'E', 'Erro ao enviar'), (b'K', 'Enviado')], default=b'S', max_length=1)),
                ('date', models.DateTimeField(default=datetime.datetime.now)),
                ('to', cms.fields.ListField()),
                ('html', models.TextField()),
            ],
            options={
                'ordering': ('-date',),
            },
        ),
        migrations.CreateModel(
            name='FileDownload',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=250, verbose_name='T\xedtulo')),
                ('file', models.FileField(upload_to=b'uploads', verbose_name='Arquivo')),
                ('count', models.IntegerField(default=0, verbose_name='Downloads')),
                ('expires_at', models.DateTimeField(blank=True, default=None, null=True, verbose_name='Data de expira\xe7\xe3o')),
                ('create_article', models.BooleanField(default=False, verbose_name=b'Cria\xc3\xa7\xc3\xa3o do Artigo')),
                ('article', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='cms.Article')),
            ],
            options={
                'verbose_name': 'Arquivo para download',
                'verbose_name_plural': 'Arquivos para download',
            },
        ),
        migrations.CreateModel(
            name='GroupItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.Group')),
            ],
            options={
                'ordering': ('grouptype__name', 'group__name'),
                'verbose_name': 'Item',
                'verbose_name_plural': 'Itens',
            },
        ),
        migrations.CreateModel(
            name='GroupType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=80, verbose_name='Nome')),
                ('order', models.PositiveIntegerField(default=1, verbose_name='Ordem')),
            ],
            options={
                'ordering': ('order',),
                'verbose_name': 'Tipo de Grupo',
                'verbose_name_plural': 'Tipos de Grupo',
            },
        ),
        migrations.CreateModel(
            name='Menu',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Nome')),
                ('link', models.CharField(blank=True, max_length=250, null=True, verbose_name='URL')),
                ('is_active', models.BooleanField(default=True, verbose_name='Est\xe1 ativo?')),
                ('lft', models.PositiveIntegerField(db_index=True, editable=False)),
                ('rght', models.PositiveIntegerField(db_index=True, editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(db_index=True, editable=False)),
                ('article', smart_selects.db_fields.ChainedForeignKey(blank=True, chained_field=b'section', chained_model_field=b'sections', default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='cms.Article', verbose_name='Artigo')),
                ('parent', mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='cms.Menu', verbose_name='Pai')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Permissao',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.Group')),
            ],
            options={
                'verbose_name': 'Permiss\xe3o',
                'verbose_name_plural': 'Permiss\xf5es',
            },
        ),
        migrations.CreateModel(
            name='Recurso',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recurso', models.CharField(choices=[('EMAIL', 'Envio de email autom\xe1tico'), ('SITE_NAME', 'Nome do Site'), ('ROBOTS', 'Permite busca pelo Google'), ('COMMENT_P', 'Texto para coment\xe1rios privados'), ('COMMENT', 'Texto para coment\xe1rios'), ('SIGNUP', 'Permite cadastro de usu\xe1rios'), ('EMAILADMIN', 'Quem recebe avisos de novos usu\xe1rios')], max_length=10, unique=True, verbose_name='Par\xe2metro')),
                ('valor', models.TextField(blank=True, null=True, verbose_name='Valor')),
                ('ativo', models.BooleanField(default=True, verbose_name='Ativo?')),
            ],
            options={
                'verbose_name': 'Par\xe2metro do Site',
                'verbose_name_plural': 'Par\xe2metros do Site',
            },
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=250, verbose_name='T\xedtulo')),
                ('slug', models.SlugField(blank=True, max_length=250, verbose_name='Slug')),
                ('header', models.TextField(blank=True, null=True, verbose_name='Descri\xe7\xe3o')),
                ('keywords', models.TextField(blank=True, default=None, null=True, verbose_name='Palavras Chaves')),
                ('order', models.PositiveIntegerField(db_index=True, default=1, help_text='0 para que a se\xe7\xe3o n\xe3o apare\xe7a em nenhuma listagem.', verbose_name='Ordem')),
                ('template', models.CharField(blank=True, max_length=250, null=True, verbose_name='Template')),
                ('views', models.IntegerField(default=0)),
                ('conversions', models.IntegerField(default=0)),
            ],
            options={
                'ordering': ['order', 'title'],
                'verbose_name': 'Se\xe7\xe3o',
                'verbose_name_plural': 'Se\xe7\xf5es',
            },
        ),
        migrations.CreateModel(
            name='SectionItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField(db_index=True, default=1, verbose_name='Ordem')),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cms.Article', verbose_name='Artigo')),
                ('section', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cms.Section', verbose_name='Se\xe7\xe3o')),
            ],
            options={
                'ordering': ['order'],
                'verbose_name': 'Artigo da se\xe7\xe3o',
                'verbose_name_plural': 'Artigos da se\xe7\xe3o',
            },
        ),
        migrations.CreateModel(
            name='Theme',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=60, verbose_name='Nome')),
                ('path_name', models.SlugField(max_length=60, unique=True, verbose_name='Pasta')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Descri\xe7\xe3o')),
                ('active', models.BooleanField(default=False, verbose_name='Ativo?')),
                ('path', models.FilePathField(editable=False, max_length=256, path=b'/media/leonardo/BACKUP/Workspace/radix/ongportal/ongportal/ongportal/media/uploads/themes', recursive=True)),
            ],
            options={
                'verbose_name': 'Temas',
                'verbose_name_plural': 'Temas',
            },
        ),
        migrations.CreateModel(
            name='URLMigrate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('old_url', models.CharField(db_index=True, max_length=250, verbose_name='URL antiga')),
                ('new_url', models.CharField(max_length=250, verbose_name='URL nova')),
                ('dtupdate', models.DateTimeField(auto_now=True, verbose_name='\xdaltima atualiza\xe7\xe3o')),
                ('views', models.IntegerField(default=0, editable=False, verbose_name='Visitas')),
                ('redirect_type', models.CharField(choices=[(b'M', 'MOVED'), (b'H', 'HOTLINK')], max_length=1, verbose_name='Tipo')),
                ('obs', models.TextField(blank=True, null=True, verbose_name='Observa\xe7\xe3o')),
            ],
            options={
                'verbose_name': 'Migra\xe7\xe3o de URL',
                'verbose_name_plural': 'Migra\xe7\xe3o de URLs',
            },
        ),
        migrations.AddField(
            model_name='section',
            name='articles',
            field=models.ManyToManyField(blank=True, null=True, through='cms.SectionItem', to='cms.Article'),
        ),
        migrations.AddField(
            model_name='permissao',
            name='section',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cms.Section'),
        ),
        migrations.AddField(
            model_name='menu',
            name='section',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='cms.Section', verbose_name='Se\xe7\xe3o'),
        ),
        migrations.AddField(
            model_name='groupitem',
            name='grouptype',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cms.GroupType'),
        ),
        migrations.AddField(
            model_name='article',
            name='sections',
            field=models.ManyToManyField(blank=True, null=True, through='cms.SectionItem', to='cms.Section'),
        ),
    ]
