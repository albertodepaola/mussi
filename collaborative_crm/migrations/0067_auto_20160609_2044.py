# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-06-09 23:44
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('collaborative_crm', '0066_notificationtone'),
    ]

    operations = [
        migrations.AddField(
            model_name='userextension',
            name='messages_tone',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='messages_tone', to='collaborative_crm.NotificationTone'),
        ),
        migrations.AddField(
            model_name='userextension',
            name='notifications_tone',
            field=models.ForeignKey(default=15, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='notifications_tone', to='collaborative_crm.NotificationTone'),
        ),
    ]
