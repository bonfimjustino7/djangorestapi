# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2020-01-23 13:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0018_auto_20200113_2353'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tipomaterial',
            name='roteiro',
        ),
        migrations.AddField(
            model_name='tipomaterial',
            name='dicas',
            field=models.TextField(null=True, verbose_name='Dicas para preenchimento'),
        ),
        migrations.AddField(
            model_name='tipomaterial',
            name='youtube',
            field=models.BooleanField(default=False, verbose_name='Youtube/Vimeo obrigatórios'),
        ),
    ]