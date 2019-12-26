# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-12-26 10:01
from __future__ import unicode_literals

from django.db import migrations
import django.db.models.deletion
import smart_selects.db_fields


class Migration(migrations.Migration):

    dependencies = [
        ('inscricao', '0011_auto_20191223_0709'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inscricao',
            name='categoria',
            field=smart_selects.db_fields.ChainedForeignKey(chained_field='premiacao', chained_model_field='premiacao', on_delete=django.db.models.deletion.PROTECT, to='base.Categoria'),
        ),
        migrations.AlterField(
            model_name='inscricao',
            name='formato',
            field=smart_selects.db_fields.ChainedForeignKey(chained_field='premiacao', chained_model_field='premiacao', on_delete=django.db.models.deletion.PROTECT, to='base.Formato'),
        ),
    ]
