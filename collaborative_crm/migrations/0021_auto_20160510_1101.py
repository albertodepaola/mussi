# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-10 14:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('collaborative_crm', '0020_auto_20160509_1526'),
    ]

    operations = [
        migrations.AddField(
            model_name='propertyextrafeatures',
            name='format',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Formato'),
        ),
        migrations.AddField(
            model_name='propertyextrafeatures',
            name='valor',
            field=models.CharField(default='', max_length=200, verbose_name='Valor'),
        ),
    ]
