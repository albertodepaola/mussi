# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-05-19 15:19
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('collaborative_crm', '0036_auto_20160519_1207'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='contact',
            options={'permissions': (('contact_assign_agents', 'Puede asignar agentes a cualquier contacto'),)},
        ),
        migrations.AlterModelOptions(
            name='property',
            options={'permissions': (('property_assign_agents', 'Puede asignar agentes a cualquier propiedad'),)},
        ),
    ]
