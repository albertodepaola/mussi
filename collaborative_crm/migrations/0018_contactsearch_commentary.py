# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-06 15:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('collaborative_crm', '0017_auto_20160506_1207'),
    ]

    operations = [
        migrations.AddField(
            model_name='contactsearch',
            name='commentary',
            field=models.CharField(blank=True, max_length=20000, null=True, verbose_name='Comentarios'),
        ),
    ]