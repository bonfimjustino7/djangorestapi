# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2020-01-13 23:53
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0017_auto_20191230_1153'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='categoria',
            name='grupo',
        ),
        migrations.AlterField(
            model_name='categoria',
            name='premiacao',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.Premiacao', verbose_name='Premiação'),
        ),
    ]
