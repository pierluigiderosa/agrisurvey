# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-01-18 15:05
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('domanda', '0002_danno'),
    ]

    operations = [
        migrations.CreateModel(
            name='Agricoltore',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('luogoNascita', models.CharField(max_length=100, verbose_name='luogo di nascita')),
                ('dataNascita', models.DateField(blank=True, null=True, verbose_name='data di nascita')),
                ('viaResidenza', models.CharField(max_length=100, verbose_name='via')),
                ('ComuneRes', models.CharField(default='', max_length=50, verbose_name='Comune di residenza')),
                ('telefono', models.CharField(blank=True, default='', max_length=50)),
                ('CF', models.CharField(default='', max_length=50)),
                ('PIva', models.CharField(default='', max_length=255, verbose_name='P. IVA')),
                ('Referente', models.CharField(blank=True, default='', max_length=255)),
                ('RefTel', models.CharField(blank=True, default='', max_length=255, verbose_name='Tel: referente')),
                ('azNome', models.CharField(blank=True, default='', max_length=255, verbose_name='Nome azienda')),
                ('azLoc', models.CharField(blank=True, default='', max_length=255, verbose_name='Localit\xe0')),
                ('azComune', models.CharField(blank=True, default='', max_length=255, verbose_name='Comune Azienda')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Agricoltore',
                'verbose_name_plural': 'Agricoltori',
            },
        ),
    ]
