# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-10 14:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('collaborative_crm', '0023_auto_20160510_1105'),
    ]

    operations = [
        migrations.AddField(
            model_name='propertyextraattribute',
            name='unit',
            field=models.CharField(blank=True, max_length=5, null=True, verbose_name='Unidad'),
        ),
    ]
