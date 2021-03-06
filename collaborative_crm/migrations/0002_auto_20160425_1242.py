# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-25 15:42
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('collaborative_crm', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=50, verbose_name='Nombre')),
                ('last_name', models.CharField(max_length=50, verbose_name='Apellido')),
                ('telephone_number', models.CharField(max_length=50, null=True, verbose_name='Tel\xe9fono')),
                ('email', models.CharField(max_length=50, null=True, verbose_name='EMail')),
                ('created', models.DateField(default=django.utils.timezone.now, verbose_name='Fecha alta')),
            ],
        ),
        migrations.CreateModel(
            name='ContactChangeLogEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Timestamp')),
                ('attribute', models.CharField(max_length=50, verbose_name='Atributo')),
                ('old_value', models.CharField(max_length=4000, null=True, verbose_name='Viejo valor')),
                ('new_value', models.CharField(max_length=4000, null=True, verbose_name='Nuevo valor')),
                ('contact', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='collaborative_crm.Contact')),
            ],
        ),
        migrations.CreateModel(
            name='ContactPropertyRelationship',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contact', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='collaborative_crm.Contact')),
            ],
        ),
        migrations.CreateModel(
            name='ContactPropertyRelationshipType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=50, verbose_name='Descripci\xf3n')),
            ],
        ),
        migrations.CreateModel(
            name='ContactSearch',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=django.utils.timezone.now, verbose_name='Fecha')),
                ('contact', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='collaborative_crm.Contact')),
            ],
        ),
        migrations.CreateModel(
            name='ContactSearchElement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attribute', models.CharField(max_length=50, verbose_name='Atributo')),
                ('values', models.CharField(max_length=1000, verbose_name='Valores')),
                ('contact_search', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='collaborative_crm.ContactSearch')),
            ],
        ),
        migrations.CreateModel(
            name='ContactStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Nombre')),
                ('description', models.CharField(default='', max_length=100, verbose_name='Descripci\xf3n')),
            ],
        ),
        migrations.CreateModel(
            name='Neighborhood',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Barrio/Zona')),
            ],
        ),
        migrations.CreateModel(
            name='Property',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('street', models.CharField(max_length=50, verbose_name='Calle')),
                ('number', models.CharField(max_length=50, null=True, verbose_name='N\xfamero')),
                ('floor', models.CharField(max_length=50, null=True, verbose_name='Piso')),
                ('apartment', models.CharField(max_length=50, null=True, verbose_name='Departamento')),
                ('intersecting_street_1', models.CharField(max_length=50, null=True, verbose_name='Entre calles 1')),
                ('intersecting_street_2', models.CharField(max_length=50, null=True, verbose_name='Entre calles 2')),
                ('anonymous_address', models.CharField(max_length=50, null=True, verbose_name='Direcci\xf3n ficticia')),
                ('for_sale', models.BooleanField(default=False, verbose_name='En venta')),
                ('sale_price', models.IntegerField(null=True, verbose_name='Precio venta')),
                ('sale_price_usd', models.IntegerField(null=True, verbose_name='Precio venta USD')),
                ('for_rent', models.BooleanField(default=False, verbose_name='En alquiler')),
                ('rent_price', models.IntegerField(null=True, verbose_name='Precio alquiler')),
                ('rent_price_usd', models.IntegerField(null=True, verbose_name='Precio alquiler USD')),
                ('expenses', models.IntegerField(null=True, verbose_name='Expensas')),
                ('rooms', models.IntegerField(null=True, verbose_name='Ambientes')),
                ('bathrooms', models.IntegerField(null=True, verbose_name='Ba\xf1os')),
                ('surface', models.IntegerField(null=True, verbose_name='Superficie total')),
                ('covered_surface', models.IntegerField(null=True, verbose_name='Superficie cubierta')),
                ('age', models.IntegerField(null=True, verbose_name='Antig\xfcedad')),
                ('description', models.CharField(default='', max_length=4000, verbose_name='Descripci\xf3n')),
            ],
        ),
        migrations.CreateModel(
            name='PropertyChangeLogEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Timestamp')),
                ('attribute', models.CharField(max_length=50, verbose_name='Atributo')),
                ('old_value', models.CharField(max_length=4000, null=True, verbose_name='Viejo valor')),
                ('new_value', models.CharField(max_length=4000, null=True, verbose_name='Nuevo valor')),
                ('property', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='collaborative_crm.Property')),
            ],
        ),
        migrations.CreateModel(
            name='PropertyExtraFeatures',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=200, verbose_name='Descripci\xf3n')),
                ('property', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='collaborative_crm.Property')),
            ],
        ),
        migrations.CreateModel(
            name='PropertyImages',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=200, verbose_name='Descripci\xf3n')),
                ('property', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='collaborative_crm.Property')),
            ],
        ),
        migrations.CreateModel(
            name='PropertyStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Nombre')),
                ('description', models.CharField(default='', max_length=100, verbose_name='Descripci\xf3n')),
            ],
        ),
        migrations.CreateModel(
            name='PropertyType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=50, verbose_name='Descripci\xf3n')),
            ],
        ),
        migrations.AddField(
            model_name='company',
            name='city',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='collaborative_crm.City'),
        ),
        migrations.AlterField(
            model_name='branch',
            name='name',
            field=models.CharField(max_length=50, verbose_name='Nombre'),
        ),
        migrations.AlterField(
            model_name='city',
            name='name',
            field=models.CharField(max_length=50, verbose_name='Ciudad'),
        ),
        migrations.AlterField(
            model_name='company',
            name='name',
            field=models.CharField(max_length=50, verbose_name='Nombre'),
        ),
        migrations.AlterField(
            model_name='country',
            name='name',
            field=models.CharField(max_length=50, verbose_name='Pa\xeds'),
        ),
        migrations.AddField(
            model_name='property',
            name='city',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='collaborative_crm.City'),
        ),
        migrations.AddField(
            model_name='property',
            name='company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='collaborative_crm.Company'),
        ),
        migrations.AddField(
            model_name='property',
            name='contacts',
            field=models.ManyToManyField(through='collaborative_crm.ContactPropertyRelationship', to='collaborative_crm.Contact'),
        ),
        migrations.AddField(
            model_name='property',
            name='neighborhood',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='collaborative_crm.Neighborhood'),
        ),
        migrations.AddField(
            model_name='property',
            name='status',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='collaborative_crm.PropertyStatus'),
        ),
        migrations.AddField(
            model_name='property',
            name='type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='collaborative_crm.PropertyType'),
        ),
        migrations.AddField(
            model_name='neighborhood',
            name='city',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='collaborative_crm.City'),
        ),
        migrations.AddField(
            model_name='contactpropertyrelationship',
            name='contact_property_relationship_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='collaborative_crm.ContactPropertyRelationshipType'),
        ),
        migrations.AddField(
            model_name='contactpropertyrelationship',
            name='property',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='collaborative_crm.Property'),
        ),
        migrations.AddField(
            model_name='contact',
            name='company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='collaborative_crm.Company'),
        ),
        migrations.AddField(
            model_name='contact',
            name='status',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='collaborative_crm.ContactStatus'),
        ),
    ]
