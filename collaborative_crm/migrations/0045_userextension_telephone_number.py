# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-05-31 16:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('collaborative_crm', '0044_auto_20160530_1523'),
    ]

    operations = [
        migrations.AddField(
            model_name='userextension',
            name='telephone_number',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Tel\xe9fono'),
        ),
    ]
