# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-05-11 06:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tunga_tasks', '0091_auto_20170509_0547'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='analytics_id',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
    ]
