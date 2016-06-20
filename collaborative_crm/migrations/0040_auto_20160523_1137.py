# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-05-23 14:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('collaborative_crm', '0039_auto_20160520_1326'),
    ]

    operations = [
        migrations.AddField(
            model_name='contactchangelogentry',
            name='proxy_class',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Clase intermediaria'),
        ),
        migrations.AddField(
            model_name='contactchangelogentry',
            name='proxy_source_field',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Campo origen de clase intermediaria'),
        ),
        migrations.AddField(
            model_name='contactchangelogentry',
            name='proxy_target_field',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Campo destino de clase intermediaria'),
        ),
    ]