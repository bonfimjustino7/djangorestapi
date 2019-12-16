# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('util', '0002_emailagendado'),
    ]

    operations = [
        migrations.CreateModel(
            name='Recurso',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recurso', models.CharField(choices=[('EMAIL', 'Envio de email automático'), ('SITE_NAME', 'Nome do Site')], max_length=10, unique=True, verbose_name='Parâmetro')),
                ('valor', models.TextField(blank=True, null=True, verbose_name='Valor')),
                ('ativo', models.BooleanField(default=True, verbose_name='Ativo?')),
            ],
            options={
                'verbose_name': 'Parâmetro do Sistema',
                'verbose_name_plural': 'Parâmetros do Sistema',
            },
        ),
    ]