# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2017-01-19 04:53
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tunga_tasks', '0040_auto_20170118_1323'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='sub_tasks', to='tunga_tasks.Task'),
        ),
    ]
