# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-03 02:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('collaborative_crm', '0013_auto_20160502_1828'),
    ]

    operations = [
        migrations.AddField(
            model_name='contactpropertyrelationship',
            name='commentary',
            field=models.CharField(blank=True, max_length=20000, null=True, verbose_name='Cometarios'),
        ),
    ]
