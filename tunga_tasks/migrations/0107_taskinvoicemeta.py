# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-06-13 03:23
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tunga_tasks', '0106_auto_20170612_0348'),
    ]

    operations = [
        migrations.CreateModel(
            name='TaskInvoiceMeta',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('meta_key', models.CharField(max_length=30)),
                ('meta_value', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('invoice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tunga_tasks.Integration')),
            ],
            options={
                'ordering': ['created_at'],
            },
        ),
    ]
