# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-07 18:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('collaborative_crm', '0056_auto_20160605_1827'),
    ]

    operations = [
        migrations.AddField(
            model_name='changelogentrytype',
            name='requires_permissions',
            field=models.BooleanField(default=False, verbose_name='Requiere permisos'),
        ),
    ]
