# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-03 12:52
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('collaborative_crm', '0014_contactpropertyrelationship_commentary'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='contactpropertyrelationship',
            name='date_added',
        ),
        migrations.AddField(
            model_name='contactpropertyrelationship',
            name='last_modified_datetime',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='\xdaltima modificaci\xf3n'),
        ),
    ]
