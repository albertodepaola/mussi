# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-02 14:19
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0007_alter_validators_add_error_messages'),
        ('collaborative_crm', '0048_usernotificationconfig'),
    ]

    operations = [
        migrations.CreateModel(
            name='GroupNotificationConfig',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notify', models.BooleanField(default=True, verbose_name='Notificarme')),
                ('email', models.BooleanField(default=True, verbose_name='Enviarme email')),
                ('can_see', models.BooleanField(default=True, verbose_name='Puede ver')),
                ('can_edit', models.BooleanField(default=True, verbose_name='Puede editar')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='collaborative_crm.Company')),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.Group')),
                ('notification_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='collaborative_crm.NotificationType')),
            ],
        ),
        migrations.AddField(
            model_name='usernotificationconfig',
            name='can_edit',
            field=models.BooleanField(default=True, verbose_name='Puede editar'),
        ),
        migrations.AddField(
            model_name='usernotificationconfig',
            name='can_see',
            field=models.BooleanField(default=True, verbose_name='Puede ver'),
        ),
    ]
