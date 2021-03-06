# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-26 22:49
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('collaborative_crm', '0002_auto_20160425_1242'),
    ]

    operations = [
        migrations.AlterField(
            model_name='branch',
            name='city',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='collaborative_crm.City'),
        ),
        migrations.AlterField(
            model_name='company',
            name='city',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='collaborative_crm.City'),
        ),
        migrations.AlterField(
            model_name='contact',
            name='email',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='EMail'),
        ),
        migrations.AlterField(
            model_name='contact',
            name='status',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='collaborative_crm.ContactStatus'),
        ),
        migrations.AlterField(
            model_name='contact',
            name='telephone_number',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Tel\xe9fono'),
        ),
        migrations.AlterField(
            model_name='contactchangelogentry',
            name='new_value',
            field=models.CharField(blank=True, max_length=4000, null=True, verbose_name='Nuevo valor'),
        ),
        migrations.AlterField(
            model_name='contactchangelogentry',
            name='old_value',
            field=models.CharField(blank=True, max_length=4000, null=True, verbose_name='Viejo valor'),
        ),
        migrations.AlterField(
            model_name='property',
            name='age',
            field=models.IntegerField(blank=True, null=True, verbose_name='Antig\xfcedad'),
        ),
        migrations.AlterField(
            model_name='property',
            name='anonymous_address',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Direcci\xf3n ficticia'),
        ),
        migrations.AlterField(
            model_name='property',
            name='apartment',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Departamento'),
        ),
        migrations.AlterField(
            model_name='property',
            name='bathrooms',
            field=models.IntegerField(blank=True, null=True, verbose_name='Ba\xf1os'),
        ),
        migrations.AlterField(
            model_name='property',
            name='city',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='collaborative_crm.City'),
        ),
        migrations.AlterField(
            model_name='property',
            name='covered_surface',
            field=models.IntegerField(blank=True, null=True, verbose_name='Superficie cubierta'),
        ),
        migrations.AlterField(
            model_name='property',
            name='expenses',
            field=models.IntegerField(blank=True, null=True, verbose_name='Expensas'),
        ),
        migrations.AlterField(
            model_name='property',
            name='floor',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Piso'),
        ),
        migrations.AlterField(
            model_name='property',
            name='intersecting_street_1',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Entre calles 1'),
        ),
        migrations.AlterField(
            model_name='property',
            name='intersecting_street_2',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Entre calles 2'),
        ),
        migrations.AlterField(
            model_name='property',
            name='neighborhood',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='collaborative_crm.Neighborhood'),
        ),
        migrations.AlterField(
            model_name='property',
            name='number',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='N\xfamero'),
        ),
        migrations.AlterField(
            model_name='property',
            name='rent_price',
            field=models.IntegerField(blank=True, null=True, verbose_name='Precio alquiler'),
        ),
        migrations.AlterField(
            model_name='property',
            name='rent_price_usd',
            field=models.IntegerField(blank=True, null=True, verbose_name='Precio alquiler USD'),
        ),
        migrations.AlterField(
            model_name='property',
            name='rooms',
            field=models.IntegerField(blank=True, null=True, verbose_name='Ambientes'),
        ),
        migrations.AlterField(
            model_name='property',
            name='sale_price',
            field=models.IntegerField(blank=True, null=True, verbose_name='Precio venta'),
        ),
        migrations.AlterField(
            model_name='property',
            name='sale_price_usd',
            field=models.IntegerField(blank=True, null=True, verbose_name='Precio venta USD'),
        ),
        migrations.AlterField(
            model_name='property',
            name='status',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='collaborative_crm.PropertyStatus'),
        ),
        migrations.AlterField(
            model_name='property',
            name='surface',
            field=models.IntegerField(blank=True, null=True, verbose_name='Superficie total'),
        ),
        migrations.AlterField(
            model_name='property',
            name='type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='collaborative_crm.PropertyType'),
        ),
        migrations.AlterField(
            model_name='propertychangelogentry',
            name='new_value',
            field=models.CharField(blank=True, max_length=4000, null=True, verbose_name='Nuevo valor'),
        ),
        migrations.AlterField(
            model_name='propertychangelogentry',
            name='old_value',
            field=models.CharField(blank=True, max_length=4000, null=True, verbose_name='Viejo valor'),
        ),
    ]
