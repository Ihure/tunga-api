# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-08-04 06:39
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import tunga_utils.validators


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tunga_tasks', '0029_auto_20160725_1323'),
    ]

    operations = [
        migrations.CreateModel(
            name='TaskInvoice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('fee', models.DecimalField(decimal_places=4, max_digits=19)),
                ('currency', models.CharField(choices=[('EUR', 'EUR'), ('USD', 'USD')], default='EUR', max_length=5)),
                ('payment_method', models.CharField(blank=True, choices=[('bitonic', 'Pay with ideal / mister cash'), ('bitcoin', 'Pay with bitcoin'), ('bank', 'Pay by bank transfer')], help_text='bitonic - Pay with ideal / mister cash,bitcoin - Pay with bitcoin,bank - Pay by bank transfer', max_length=30, null=True)),
                ('btc_address', models.CharField(max_length=40, validators=[tunga_utils.validators.validate_btc_address])),
                ('btc_price', models.DecimalField(blank=True, decimal_places=8, max_digits=18, null=True)),
                ('invoice_number', models.CharField(blank=True, max_length=20, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='client_invoices', to=settings.AUTH_USER_MODEL)),
                ('developer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='developer_invoices', to=settings.AUTH_USER_MODEL)),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tunga_tasks.Task')),
            ],
            options={
                'ordering': ['created_at'],
            },
        ),
    ]