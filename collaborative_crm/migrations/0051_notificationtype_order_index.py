# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-03 14:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('collaborative_crm', '0050_auto_20160603_1104'),
    ]

    operations = [
        migrations.AddField(
            model_name='notificationtype',
            name='order_index',
            field=models.IntegerField(blank=True, null=True, verbose_name='Orden'),
        ),
    ]
