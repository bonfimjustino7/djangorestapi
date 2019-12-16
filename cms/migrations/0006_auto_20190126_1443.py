# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2019-01-26 14:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0005_auto_20190119_0908'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recurso',
            name='recurso',
            field=models.CharField(choices=[('EMAIL', 'Envio de email autom\xe1tico'), ('SITE_NAME', 'Nome do Site'), ('ROBOTS', 'Permite busca pelo Google'), ('COMMENT_P', 'Texto para coment\xe1rios privados'), ('COMMENT', 'Texto para coment\xe1rios'), ('SIGNUP', 'Permite cadastro de usu\xe1rios'), ('EMAILADMIN', 'Quem recebe avisos de novos usu\xe1rios'), ('CP_ANUAL', 'C\xf3digo do Plano Anual'), ('CP_MENSAL', 'C\xf3digo do Plano Mensal')], max_length=10, unique=True, verbose_name='Par\xe2metro'),
        ),
    ]