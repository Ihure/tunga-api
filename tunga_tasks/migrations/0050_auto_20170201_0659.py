# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2017-02-01 06:59
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tunga_tasks', '0049_auto_20170201_0420'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='progressevent',
            options={'ordering': ['-due_at']},
        ),
    ]
