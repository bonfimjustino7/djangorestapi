# Generated by Django 2.1.7 on 2019-03-28 00:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0004_auto_20190327_2347'),
    ]

    operations = [
        migrations.CreateModel(
            name='UF',
            fields=[
                ('sigla', models.CharField(max_length=2, primary_key=True, serialize=False)),
                ('nome', models.CharField(max_length=40)),
            ],
        ),
    ]
