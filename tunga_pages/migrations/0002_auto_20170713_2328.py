# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-07-13 23:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tunga_pages', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='skillpageprofile',
            options={'ordering': ['-priority', '-created_at'], 'verbose_name': 'skill profile'},
        ),
        migrations.AlterField(
            model_name='skillpage',
            name='pitch_body',
            field=models.CharField(max_length=450),
        ),
    ]
