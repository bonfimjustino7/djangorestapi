# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-04-20 12:44
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inscricao', '0003_auto_20190417_2005'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='material',
            name='inscricao',
        ),
        migrations.RemoveField(
            model_name='material',
            name='tipo',
        ),
        migrations.DeleteModel(
            name='Material',
        ),
        migrations.DeleteModel(
            name='TipoMaterial',
        ),
    ]
