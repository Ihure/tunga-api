# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-08-01 14:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tunga_profiles', '0011_userprofile_id_document'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='postal_code',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
