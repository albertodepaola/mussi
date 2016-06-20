# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-06-19 00:52
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('collaborative_crm', '0068_auto_20160615_2038'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContactWorkflow',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Nombre')),
                ('description', models.CharField(default='', max_length=4000, verbose_name='Descripci\xf3n')),
                ('is_active', models.BooleanField(default=False, verbose_name='Activo')),
                ('is_default', models.BooleanField(default=False, verbose_name='Default')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='collaborative_crm.Company')),
            ],
        ),
        migrations.CreateModel(
            name='ContactWorkflowAction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Nombre')),
                ('automatic_time', models.IntegerField(blank=True, null=True, verbose_name='Tiempo')),
                ('automatic_unit', models.CharField(blank=True, max_length=1, null=True, verbose_name='Unidad')),
                ('is_inverse', models.BooleanField(default=False, verbose_name='Inversa')),
            ],
        ),
        migrations.CreateModel(
            name='ContactWorkflowState',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Nombre')),
                ('position', models.CharField(default='[0, 0]', max_length=50, verbose_name='Posici\xf3n')),
                ('color', models.CharField(default='[0, 0, 0]', max_length=50, verbose_name='Color')),
                ('workflow', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='collaborative_crm.ContactWorkflow')),
            ],
        ),
        migrations.AlterField(
            model_name='contact',
            name='status',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='collaborative_crm.ContactWorkflowState'),
        ),
        migrations.DeleteModel(
            name='ContactStatus',
        ),
        migrations.AddField(
            model_name='contactworkflowaction',
            name='source_state',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='source_state', to='collaborative_crm.ContactWorkflowState'),
        ),
        migrations.AddField(
            model_name='contactworkflowaction',
            name='target_state',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='target_state', to='collaborative_crm.ContactWorkflowState'),
        ),
    ]
