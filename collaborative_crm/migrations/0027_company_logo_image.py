# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-05-16 16:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('collaborative_crm', '0026_auto_20160510_1311'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='logo_image',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Logo'),
        ),
    ]