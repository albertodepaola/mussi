# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-10 14:03
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('collaborative_crm', '0021_auto_20160510_1101'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='PropertyExtraFeatures',
            new_name='PropertyExtraAttribute',
        ),
    ]