# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-04-09 17:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tunga_auth', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='tungauser',
            name='last_activity',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
