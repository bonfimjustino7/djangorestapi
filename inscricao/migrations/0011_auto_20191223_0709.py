# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-12-23 07:09
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import smart_selects.db_fields


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0014_auto_20191223_0709'),
        ('inscricao', '0010_auto_20191007_0830'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='material',
            options={'verbose_name': 'Material', 'verbose_name_plural': 'Materiais'},
        ),
        migrations.AddField(
            model_name='inscricao',
            name='premiacao',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='base.Premiacao'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='inscricao',
            name='agencia',
            field=smart_selects.db_fields.ChainedForeignKey(chained_field='empresa', chained_model_field='empresa', on_delete=django.db.models.deletion.CASCADE, to='inscricao.EmpresaAgencia'),
        ),
        migrations.AlterField(
            model_name='inscricao',
            name='formato',
            field=smart_selects.db_fields.ChainedForeignKey(chained_field='premio', chained_model_field='premio', default=1, on_delete=django.db.models.deletion.PROTECT, to='base.Formato'),
            preserve_default=False,
        ),
    ]
