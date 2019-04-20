# Generated by Django 2.1.7 on 2019-04-16 15:07

import datetime
from django.db import migrations, models
import util.fields


class Migration(migrations.Migration):

    dependencies = [
        ('util', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailAgendado',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(default='', max_length=90)),
                ('status', models.CharField(choices=[('A', 'Aguardando envio manual...'), ('S', 'Enviando...'), ('R', 'Re-enviando'), ('E', 'Erro ao enviar'), ('K', 'Enviado')], default='S', max_length=1)),
                ('date', models.DateTimeField(default=datetime.datetime.now)),
                ('to', models.TextField()),
                ('html', models.TextField()),
            ],
            options={
                'ordering': ('-date',),
            },
        ),
    ]