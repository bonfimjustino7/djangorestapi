# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2020-01-30 16:07
from __future__ import unicode_literals

from django.db import migrations, models
import inscricao.models


class Migration(migrations.Migration):

    dependencies = [
        ('inscricao', '0017_auto_20200123_1313'),
    ]

    operations = [
        migrations.AddField(
            model_name='inscricao',
            name='apresentacao',
            field=models.URLField(blank=True, max_length=512, null=True, verbose_name='Apresentação'),
        ),
        migrations.AddField(
            model_name='inscricao',
            name='videocase',
            field=models.URLField(blank=True, max_length=512, null=True, verbose_name='Videocase'),
        ),
        migrations.AlterField(
            model_name='material',
            name='arquivo',
            field=inscricao.models.FileField(blank=True, max_length=512, null=True, upload_to=inscricao.models.path),
        ),
    ]