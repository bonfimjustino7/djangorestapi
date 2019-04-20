# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-04-20 13:00
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0008_auto_20190420_1244'),
        ('inscricao', '0004_auto_20190420_1244'),
    ]

    operations = [
        migrations.CreateModel(
            name='Material',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('arquivo', models.FileField(blank=True, null=True, upload_to='')),
                ('url', models.URLField(blank=True, null=True)),
                ('idsoundcloud', models.CharField(blank=True, max_length=20, null=True)),
                ('inscricao', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inscricao.Inscricao')),
                ('tipo', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='base.TipoMaterial')),
            ],
            options={
                'verbose_name': 'Material',
                'verbose_name_plural': 'Materiais',
                'ordering': ('tipo',),
            },
        ),
    ]
